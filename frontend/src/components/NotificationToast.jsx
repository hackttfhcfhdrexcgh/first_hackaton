// filepath: frontend/src/components/NotificationToast.jsx
export default function NotificationToast({ notification }) {
  if (!notification || !notification.show) return null;

  const { hexUnlocked, reward, achievements, progress, error } = notification;

  return (
    <>
      <style>{`
        @keyframes slideDown {
          from { transform: translateY(-20px); opacity: 0; }
          to   { transform: translateY(0);     opacity: 1; }
        }
        .fow-toast {
          animation: slideDown 0.3s ease-out;
        }
      `}</style>
      <div
        className="fow-toast"
        style={{
          position: "absolute",
          top: 12,
          left: 0,
          right: 0,
          zIndex: 1000,
          pointerEvents: "none",
        }}
      >
        <div
          style={{
            background: "#0d0d1a",
            border: "1px solid #00C4FF",
            borderRadius: 12,
            padding: 16,
            maxWidth: 280,
            margin: "12px auto",
            color: "#00C4FF",
            boxShadow: "0 4px 20px rgba(0, 196, 255, 0.25)",
            pointerEvents: "auto",
          }}
        >
          {error && (
            <div style={{ color: "#ff4d6d", fontSize: 13 }}>⚠ {error}</div>
          )}

          {hexUnlocked && (
            <>
              <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 6 }}>
                🗺 Территория открыта!
              </div>
              {reward && reward.label && (
                <div style={{ color: "#fff", fontSize: 13, marginBottom: 6 }}>
                  🎁 {reward.label}
                </div>
              )}
            </>
          )}

          {achievements && achievements.length > 0 && (
            <div style={{ marginTop: hexUnlocked ? 8 : 0 }}>
              {achievements.map((a) => (
                <div
                  key={a.code}
                  style={{
                    fontSize: 12,
                    color: "#ffd166",
                    marginBottom: 2,
                  }}
                >
                  ★ Ачивка: {a.name} — {a.reward_label}
                </div>
              ))}
            </div>
          )}

          {!hexUnlocked && !error && progress && (
            <div style={{ fontSize: 13, color: "#ccc" }}>
              Прогресс: {progress.current}/{progress.target} — {progress.description}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
