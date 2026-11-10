package com.genshinhelper.lite;

import android.app.*;
import android.content.Context;
import android.content.Intent;
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
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.TextView;
import androidx.annotation.Nullable;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;
import com.google.mlkit.nl.translate.Translation;
import com.google.mlkit.nl.translate.Translator;
import com.google.mlkit.nl.translate.TranslatorOptions;
import com.google.mlkit.common.model.DownloadConditions;
import java.util.concurrent.atomic.AtomicBoolean;

public class CaptureService extends Service {
    private MediaProjection projection;
    private VirtualDisplay display;
    private ImageReader reader;
    private HandlerThread thread;
    private Handler handler;
    private TextRecognizer recognizer;
    private Translator translator;
    private TextView bubble;
    private WindowManager windowManager;
    private final AtomicBoolean busy = new AtomicBoolean(false);
    private long lastFrame;
    private int screenWidth, screenHeight, density;

    @Override public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        startForeground(7, new Notification.Builder(this, "capture")
            .setContentTitle("Genshin Assistant") .setContentText("الترجمة المباشرة قيد التشغيل")
            .setSmallIcon(android.R.drawable.ic_menu_view).setOngoing(true).build());
        recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
        TranslatorOptions options = new TranslatorOptions.Builder().setSourceLanguage("en").setTargetLanguage("ar").build();
        translator = Translation.getClient(options);
        translator.downloadModelIfNeeded(new DownloadConditions.Builder().build());
        showBubble("بانتظار نص إنجليزي ظاهر على الشاشة…");
        thread = new HandlerThread("screen-ocr"); thread.start(); handler = new Handler(thread.getLooper());
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null || !intent.hasExtra("data")) { stopSelf(); return START_NOT_STICKY; }
        try {
            int resultCode = intent.getIntExtra("resultCode", Activity.RESULT_CANCELED);
            Intent data = intent.getParcelableExtra("data");
            MediaProjectionManager manager = (MediaProjectionManager)getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            projection = manager.getMediaProjection(resultCode, data);
            if (projection == null) { showBubble("تعذر بدء التقاط الشاشة"); stopSelf(); return START_NOT_STICKY; }
            android.util.DisplayMetrics metrics = getResources().getDisplayMetrics();
            screenWidth = metrics.widthPixels; screenHeight = metrics.heightPixels; density = metrics.densityDpi;
            reader = ImageReader.newInstance(screenWidth, screenHeight, PixelFormat.RGBA_8888, 2);
            reader.setOnImageAvailableListener(this::processFrame, handler);
            projection.registerCallback(new MediaProjection.Callback() { @Override public void onStop() { stopSelf(); } }, handler);
            display = projection.createVirtualDisplay("GenshinLiveOCR", screenWidth, screenHeight, density, DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, reader.getSurface(), null, handler);
        } catch (Exception e) { showBubble("خطأ في الالتقاط: " + e.getClass().getSimpleName()); stopSelf(); }
        return START_NOT_STICKY;
    }

    private void processFrame(ImageReader source) {
        Image image = null;
        try {
            image = source.acquireLatestImage();
            if (image == null || busy.get() || System.currentTimeMillis() - lastFrame < 1400) { if (image != null) image.close(); return; }
            busy.set(true); lastFrame = System.currentTimeMillis();
            Image frame = image;
            recognizer.process(InputImage.fromMediaImage(frame, 0))
                .addOnSuccessListener(result -> {
                    String text = result.getText();
                    if (text == null || text.trim().isEmpty()) { busy.set(false); return; }
                    translator.translate(text).addOnSuccessListener(ar -> showBubble(ar))
                        .addOnFailureListener(err -> showBubble("تعذر تنزيل/تشغيل نموذج الترجمة. افتح الإنترنت ثم أعد المحاولة."))
                        .addOnCompleteListener(task -> busy.set(false));
                }).addOnFailureListener(err -> busy.set(false))
                .addOnCompleteListener(task -> { try { frame.close(); } catch (Exception ignored) {} });
            image = null;
        } catch (Exception e) { busy.set(false); }
        finally { if (image != null) image.close(); }
    }

    private void showBubble(String value) {
        if (!Settings.canDrawOverlays(this)) return;
        new Handler(getMainLooper()).post(() -> {
            try {
                if (windowManager == null) windowManager = (WindowManager)getSystemService(WINDOW_SERVICE);
                if (bubble == null) {
                    bubble = new TextView(this); bubble.setTextColor(0xFFFFFFFF); bubble.setTextSize(14); bubble.setPadding(18, 12, 18, 12); bubble.setBackgroundColor(0xDD20202A);
                    WindowManager.LayoutParams p = new WindowManager.LayoutParams(Math.min(screenWidth > 0 ? screenWidth - 32 : 600, 760), WindowManager.LayoutParams.WRAP_CONTENT, Build.VERSION.SDK_INT >= 26 ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY : WindowManager.LayoutParams.TYPE_PHONE, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN, PixelFormat.TRANSLUCENT);
                    p.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL; p.y = 90; windowManager.addView(bubble, p);
                }
                bubble.setText(value.length() > 1800 ? value.substring(0,1800) : value);
            } catch (Exception ignored) { }
        });
    }
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= 26) { NotificationChannel channel = new NotificationChannel("capture", "Screen capture", NotificationManager.IMPORTANCE_LOW); ((NotificationManager)getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(channel); }
    }
    @Override public void onDestroy() {
        try { if (display != null) display.release(); if (reader != null) reader.close(); if (projection != null) projection.stop(); if (windowManager != null && bubble != null) windowManager.removeView(bubble); if (recognizer != null) recognizer.close(); if (translator != null) translator.close(); if (thread != null) thread.quitSafely(); } catch (Exception ignored) { }
        super.onDestroy();
    }
    @Nullable @Override public IBinder onBind(Intent intent) { return null; }
}
