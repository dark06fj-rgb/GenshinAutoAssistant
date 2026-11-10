package com.genshinhelper.lite;

import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.graphics.Bitmap;
import android.graphics.PixelFormat;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Build;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.provider.Settings;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.core.app.ServiceCompat;

import com.google.mlkit.common.model.DownloadConditions;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;
import com.google.mlkit.nl.translate.Translation;
import com.google.mlkit.nl.translate.Translator;
import com.google.mlkit.nl.translate.TranslatorOptions;

import java.nio.ByteBuffer;
import java.util.concurrent.atomic.AtomicBoolean;

public class CaptureService extends Service {
    private static final String TAG = "GenshinTranslate";
    private static final String CHANNEL_ID = "capture";
    private static final int NOTIFICATION_ID = 7;
    private static final long FRAME_INTERVAL_MS = 1200L;
    private static final int MAX_TRANSLATION_CHUNK = 900;

    private MediaProjection projection;
    private VirtualDisplay display;
    private ImageReader reader;
    private HandlerThread workerThread;
    private Handler worker;
    private TextRecognizer recognizer;
    private Translator translator;
    private TextView bubble;
    private WindowManager windowManager;
    private WindowManager.LayoutParams bubbleParams;
    private DisplayManager displayManager;
    private DisplayManager.DisplayListener displayListener;

    private final AtomicBoolean busy = new AtomicBoolean(false);
    private volatile boolean translatorReady;
    private boolean projectionStarted;
    private long lastFrameTime;
    private volatile String lastTranslatedText = "";
    private int screenWidth;
    private int screenHeight;
    private int densityDpi;

    @Override
    public void onCreate() {
        super.onCreate();
        Log.i(TAG, "Service onCreate");
        createNotificationChannel();
        startForegroundWithProjectionType();

        recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
        TranslatorOptions options = new TranslatorOptions.Builder()
                .setSourceLanguage("en")
                .setTargetLanguage("ar")
                .build();
        translator = Translation.getClient(options);

        workerThread = new HandlerThread("genshin-screen-ocr");
        workerThread.start();
        worker = new Handler(workerThread.getLooper());

        downloadTranslationModel();
        registerDisplayListener();
    }

    private void startForegroundWithProjectionType() {
        Notification notification = new Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("Genshin Assistant")
                .setContentText("الترجمة المباشرة قيد التشغيل")
                .setSmallIcon(android.R.drawable.ic_menu_view)
                .setOngoing(true)
                .build();

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ServiceCompat.startForeground(
                    this,
                    NOTIFICATION_ID,
                    notification,
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
            );
        } else {
            startForeground(NOTIFICATION_ID, notification);
        }
        Log.i(TAG, "Foreground service started with mediaProjection type when supported");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.i(TAG, "onStartCommand");
        if (intent == null || !intent.hasExtra("data")) {
            Log.e(TAG, "Missing MediaProjection permission result");
            stopSelf(startId);
            return START_NOT_STICKY;
        }
        if (projectionStarted) {
            Log.w(TAG, "Projection already active; ignoring duplicate start");
            return START_NOT_STICKY;
        }

        try {
            int resultCode = intent.getIntExtra("resultCode", Activity.RESULT_CANCELED);
            Intent permissionData;
            if (Build.VERSION.SDK_INT >= 33) {
                permissionData = intent.getParcelableExtra("data", Intent.class);
            } else {
                //noinspection deprecation
                permissionData = intent.getParcelableExtra("data");
            }
            if (resultCode != Activity.RESULT_OK || permissionData == null) {
                throw new IllegalStateException("Screen-capture permission data is invalid");
            }

            MediaProjectionManager manager = (MediaProjectionManager)
                    getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            projection = manager.getMediaProjection(resultCode, permissionData);
            if (projection == null) {
                throw new IllegalStateException("MediaProjection is null");
            }

            projection.registerCallback(new MediaProjection.Callback() {
                @Override
                public void onStop() {
                    Log.i(TAG, "MediaProjection stopped by system");
                    stopSelf();
                }
            }, worker);

            projectionStarted = true;
            createVirtualDisplayOnce();
            Log.i(TAG, "VirtualDisplay created successfully");
        } catch (Exception e) {
            Log.e(TAG, "Unable to start screen capture", e);
            showBubble("تعذر بدء التقاط الشاشة: " + e.getClass().getSimpleName());
            stopSelf(startId);
        }
        return START_NOT_STICKY;
    }

    private void readDisplayMetrics() {
        DisplayMetrics metrics = getResources().getDisplayMetrics();
        screenWidth = metrics.widthPixels;
        screenHeight = metrics.heightPixels;
        densityDpi = metrics.densityDpi;
    }

    private ImageReader createReader(int width, int height) {
        ImageReader newReader = ImageReader.newInstance(
                width, height, PixelFormat.RGBA_8888, 2);
        newReader.setOnImageAvailableListener(this::processFrame, worker);
        return newReader;
    }

    private void createVirtualDisplayOnce() {
        readDisplayMetrics();
        reader = createReader(screenWidth, screenHeight);
        display = projection.createVirtualDisplay(
                "GenshinLiveOCR",
                screenWidth,
                screenHeight,
                densityDpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                reader.getSurface(),
                null,
                worker
        );
        if (display == null) {
            throw new IllegalStateException("VirtualDisplay creation returned null");
        }
        Log.i(TAG, "Capture surface ready: " + screenWidth + "x" + screenHeight);
    }

    private void registerDisplayListener() {
        displayManager = (DisplayManager) getSystemService(Context.DISPLAY_SERVICE);
        displayListener = new DisplayManager.DisplayListener() {
            @Override public void onDisplayAdded(int displayId) { }

            @Override public void onDisplayRemoved(int displayId) { }

            @Override
            public void onDisplayChanged(int displayId) {
                if (displayId == android.view.Display.DEFAULT_DISPLAY) {
                    resizeExistingVirtualDisplay();
                }
            }
        };
        displayManager.registerDisplayListener(displayListener, worker);
    }

    /*
     * MediaProjection is intentionally used to create only one VirtualDisplay per
     * consent token. On configuration changes, resize that display and replace its
     * ImageReader surface instead of calling createVirtualDisplay() a second time.
     */
    private void resizeExistingVirtualDisplay() {
        if (display == null || projection == null || worker == null) return;
        readDisplayMetrics();
        if (reader != null
                && reader.getWidth() == screenWidth
                && reader.getHeight() == screenHeight) {
            return;
        }

        Log.i(TAG, "Display size changed; resizing existing VirtualDisplay");
        ImageReader oldReader = reader;
        ImageReader newReader = null;
        try {
            newReader = createReader(screenWidth, screenHeight);
            display.resize(screenWidth, screenHeight, densityDpi);
            display.setSurface(newReader.getSurface());
            reader = newReader;
            if (oldReader != null) oldReader.close();
            Log.i(TAG, "VirtualDisplay resized to " + screenWidth + "x" + screenHeight);
        } catch (Exception e) {
            if (newReader != null) newReader.close();
            Log.e(TAG, "Unable to resize VirtualDisplay", e);
        }
    }

    private void processFrame(ImageReader source) {
        Image image = null;
        try {
            image = source.acquireLatestImage();
            if (image == null) return;

            long now = System.currentTimeMillis();
            if (busy.get() || !translatorReady
                    || now - lastFrameTime < FRAME_INTERVAL_MS) {
                image.close();
                return;
            }

            busy.set(true);
            lastFrameTime = now;
            Bitmap bitmap = imageToBitmap(image);
            image.close();
            image = null;

            if (bitmap == null) {
                Log.e(TAG, "Could not convert captured RGBA frame to Bitmap");
                busy.set(false);
                return;
            }

            InputImage input = InputImage.fromBitmap(bitmap, 0);
            recognizer.process(input)
                    .addOnSuccessListener(result -> {
                        String extracted = result.getText();
                        if (extracted == null || extracted.trim().isEmpty()) {
                            Log.d(TAG, "OCR completed: no text found");
                            busy.set(false);
                            return;
                        }
                        Log.i(TAG, "OCR text: " + preview(extracted, 100));
                        translateText(extracted);
                    })
                    .addOnFailureListener(error -> {
                        Log.e(TAG, "OCR failed", error);
                        showBubble("تعذر قراءة النص من الشاشة");
                        busy.set(false);
                    })
                    .addOnCompleteListener(task -> bitmap.recycle());
        } catch (Exception e) {
            Log.e(TAG, "processFrame failed", e);
            if (image != null) {
                try { image.close(); } catch (Exception ignored) { }
            }
            busy.set(false);
        }
    }

    private Bitmap imageToBitmap(Image image) {
        if (image.getFormat() != PixelFormat.RGBA_8888) {
            Log.e(TAG, "Unexpected ImageReader format: " + image.getFormat());
            return null;
        }
        Image.Plane[] planes = image.getPlanes();
        if (planes == null || planes.length == 0) return null;

        Image.Plane plane = planes[0];
        ByteBuffer buffer = plane.getBuffer();
        int pixelStride = plane.getPixelStride();
        int rowStride = plane.getRowStride();
        int width = image.getWidth();
        int height = image.getHeight();

        if (pixelStride <= 0 || rowStride < width * pixelStride) return null;
        int paddedWidth = rowStride / pixelStride;
        if (paddedWidth < width) return null;

        Bitmap padded = Bitmap.createBitmap(
                paddedWidth, height, Bitmap.Config.ARGB_8888);
        buffer.rewind();
        padded.copyPixelsFromBuffer(buffer);

        if (paddedWidth == width) return padded;
        Bitmap cropped = Bitmap.createBitmap(padded, 0, 0, width, height);
        padded.recycle();
        return cropped;
    }

    private void translateText(String text) {
        String normalized = text.trim();
        if (normalized.isEmpty()) {
            busy.set(false);
            return;
        }
        if (normalized.equals(lastTranslatedText)) {
            Log.d(TAG, "Skipping unchanged OCR text");
            busy.set(false);
            return;
        }
        lastTranslatedText = normalized;

        String[] chunks = splitText(normalized, MAX_TRANSLATION_CHUNK);
        translateChunkAt(chunks, 0, new StringBuilder());
    }

    private String[] splitText(String text, int maxLength) {
        java.util.ArrayList<String> chunks = new java.util.ArrayList<>();
        int start = 0;
        while (start < text.length()) {
            int end = Math.min(start + maxLength, text.length());
            if (end < text.length()) {
                int boundary = text.lastIndexOf('\n', end);
                if (boundary > start + maxLength / 2) {
                    end = boundary + 1;
                } else {
                    boundary = text.lastIndexOf(' ', end);
                    if (boundary > start + maxLength / 2) end = boundary + 1;
                }
            }
            chunks.add(text.substring(start, end));
            start = end;
        }
        return chunks.toArray(new String[0]);
    }

    private void translateChunkAt(String[] chunks, int index, StringBuilder output) {
        if (index >= chunks.length) {
            String translated = output.toString().trim();
            if (translated.isEmpty()) {
                Log.w(TAG, "Translation completed with empty result");
                showBubble("لم تُنتج الترجمة نصاً. تحقق من النص الظاهر.");
            } else {
                Log.i(TAG, "Translation result: " + preview(translated, 120));
                showBubble(translated);
            }
            busy.set(false);
            return;
        }

        translator.translate(chunks[index])
                .addOnSuccessListener(result -> {
                    if (result != null && !result.trim().isEmpty()) {
                        if (output.length() > 0) output.append('\n');
                        output.append(result.trim());
                    }
                    translateChunkAt(chunks, index + 1, output);
                })
                .addOnFailureListener(error -> {
                    Log.e(TAG, "Translation failed for chunk " + index, error);
                    showBubble("فشلت الترجمة. تحقق من اتصال الإنترنت ونموذج اللغة.");
                    busy.set(false);
                });
    }

    private String preview(String value, int maxLength) {
        if (value == null) return "";
        return value.length() <= maxLength
                ? value : value.substring(0, maxLength) + "…";
    }

    private void downloadTranslationModel() {
        translatorReady = false;
        Log.i(TAG, "Downloading/checking English-Arabic translation model");
        showBubble("جارٍ تجهيز نموذج الترجمة…");
        translator.downloadModelIfNeeded(new DownloadConditions.Builder().build())
                .addOnSuccessListener(unused -> {
                    translatorReady = true;
                    Log.i(TAG, "Translation model ready");
                    showBubble("نموذج الترجمة جاهز. بانتظار نص إنجليزي…");
                })
                .addOnFailureListener(error -> {
                    translatorReady = false;
                    Log.e(TAG, "Translation model download failed", error);
                    showBubble("تعذر تنزيل نموذج الترجمة. تحقق من الإنترنت ثم أعد تشغيل الخدمة.");
                });
    }

    private void showBubble(String value) {
        if (!Settings.canDrawOverlays(this)) {
            Log.w(TAG, "Overlay permission not granted");
            return;
        }
        new Handler(getMainLooper()).post(() -> {
            try {
                if (windowManager == null) {
                    windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
                }
                if (bubble == null) {
                    bubble = new TextView(this);
                    bubble.setTextColor(0xFFFFFFFF);
                    bubble.setTextSize(16);
                    bubble.setPadding(24, 16, 24, 16);
                    bubble.setBackgroundColor(0xDD20202A);
                    bubble.setTextDirection(View.TEXT_DIRECTION_RTL);
                    bubble.setGravity(Gravity.CENTER);
                    bubble.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);

                    int availableWidth = screenWidth > 0 ? screenWidth - 32 : 600;
                    int width = Math.max(240, Math.min(availableWidth, 760));
                    bubbleParams = new WindowManager.LayoutParams(
                            width,
                            WindowManager.LayoutParams.WRAP_CONTENT,
                            Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                                    ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                                    : WindowManager.LayoutParams.TYPE_PHONE,
                            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                                    | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
                                    | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                            PixelFormat.TRANSLUCENT
                    );
                    bubbleParams.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL;
                    bubbleParams.y = 120;

                    bubble.setOnTouchListener(new View.OnTouchListener() {
                        private int startX;
                        private int startY;
                        private float touchX;
                        private float touchY;

                        @Override
                        public boolean onTouch(View view, MotionEvent event) {
                            switch (event.getAction()) {
                                case MotionEvent.ACTION_DOWN:
                                    startX = bubbleParams.x;
                                    startY = bubbleParams.y;
                                    touchX = event.getRawX();
                                    touchY = event.getRawY();
                                    return true;
                                case MotionEvent.ACTION_MOVE:
                                    bubbleParams.x = startX + (int) (event.getRawX() - touchX);
                                    bubbleParams.y = Math.max(0, startY
                                            + (int) (event.getRawY() - touchY));
                                    try {
                                        windowManager.updateViewLayout(bubble, bubbleParams);
                                    } catch (Exception e) {
                                        Log.e(TAG, "Unable to move overlay", e);
                                    }
                                    return true;
                                case MotionEvent.ACTION_UP:
                                case MotionEvent.ACTION_CANCEL:
                                    return true;
                                default:
                                    return false;
                            }
                        }
                    });
                    windowManager.addView(bubble, bubbleParams);
                }
                bubble.setText(value == null ? "" : preview(value, 1800));
            } catch (Exception e) {
                Log.e(TAG, "Unable to display translation overlay", e);
            }
        });
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID, "Screen capture", NotificationManager.IMPORTANCE_LOW);
            NotificationManager manager =
                    (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            manager.createNotificationChannel(channel);
        }
    }

    @Override
    public void onDestroy() {
        Log.i(TAG, "Service onDestroy - cleaning up");
        try {
            if (displayManager != null && displayListener != null) {
                displayManager.unregisterDisplayListener(displayListener);
            }
        } catch (Exception e) {
            Log.w(TAG, "Display listener cleanup failed", e);
        }
        try {
            if (display != null) {
                display.setSurface(null);
                display.release();
                display = null;
            }
        } catch (Exception e) {
            Log.w(TAG, "VirtualDisplay cleanup failed", e);
        }
        try {
            if (reader != null) {
                reader.close();
                reader = null;
            }
        } catch (Exception e) {
            Log.w(TAG, "ImageReader cleanup failed", e);
        }
        try {
            if (projection != null) {
                projection.stop();
                projection = null;
            }
        } catch (Exception e) {
            Log.w(TAG, "MediaProjection cleanup failed", e);
        }
        try {
            if (windowManager != null && bubble != null) {
                windowManager.removeView(bubble);
                bubble = null;
                bubbleParams = null;
            }
        } catch (Exception e) {
            Log.w(TAG, "Overlay cleanup failed", e);
        }
        try {
            if (recognizer != null) {
                recognizer.close();
                recognizer = null;
            }
            if (translator != null) {
                translator.close();
                translator = null;
            }
        } catch (Exception e) {
            Log.w(TAG, "ML Kit cleanup failed", e);
        }
        try {
            if (workerThread != null) {
                workerThread.quitSafely();
                workerThread = null;
                worker = null;
            }
        } catch (Exception e) {
            Log.w(TAG, "Worker cleanup failed", e);
        }
        super.onDestroy();
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}