// filepath: frontend/src/components/DemoPanel.jsx
const btnStyle = {
  background: "#1a1a2e",
  color: "#00C4FF",
  border: "1px solid #00C4FF",
  borderRadius: 8,
  padding: "8px 14px",
  fontSize: 13,
  cursor: "pointer",
  transition: "all 0.15s ease",
  fontFamily: "inherit",
};

function DemoButton({ children, onClick }) {
  return (
    <button
      style={btnStyle}
      onClick={onClick}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "#00C4FF";
        e.currentTarget.style.color = "#0d0d1a";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "#1a1a2e";
        e.currentTarget.style.color = "#00C4FF";
      }}
    >
      {children}
    </button>
  );
}

export default function DemoPanel({ stats, activeQuest, achievements, submitTx }) {
  const percent = activeQuest
    ? Math.min(100, Math.round((activeQuest.current / Math.max(1, activeQuest.target)) * 100))
    : 0;

  return (
    <div
      style={{
        background: "#0d0d1a",
        borderTop: "1px solid #00C4FF",
        padding: 12,
        color: "#00C4FF",
      }}
    >
      <div style={{ color: "#888", fontSize: 11, marginBottom: 8 }}>
        DEMO MODE · Открыто {stats?.unlocked ?? 0}/{stats?.total ?? 37} территорий
      </div>

      {activeQuest && (
        <div style={{ marginBottom: 10 }}>
          <div style={{ fontSize: 12, color: "#ccc", marginBottom: 4 }}>
            {activeQuest.description}: {activeQuest.current}/{activeQuest.target}
          </div>
          <div
            style={{
              background: "#1a1a2e",
              height: 4,
              borderRadius: 2,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${percent}%`,
                height: "100%",
                background: "#00C4FF",
                transition: "width 0.4s ease",
              }}
            />
          </div>
        </div>
      )}

      {achievements && achievements.length > 0 && (
        <div style={{ marginBottom: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
          {achievements.map((a) => (
            <span
              key={a.code}
              title={`${a.name}${a.description ? " — " + a.description : ""}`}
              style={{
                background: "#1a1a2e",
                border: "1px solid #00C4FF",
                borderRadius: 12,
                padding: "2px 8px",
                fontSize: 11,
                color: "#00C4FF",
              }}
            >
              ★ {a.name}
            </span>
          ))}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <DemoButton onClick={() => submitTx("5812", 25, "Лидо")}>
          🍕 Ресторан 25 BYN
        </DemoButton>
        <DemoButton onClick={() => submitTx("5411", 15, "Евроопт")}>
          🛒 Продукты 15 BYN
        </DemoButton>
        <DemoButton onClick={() => submitTx("5541", 40, "А-100")}>
          ⛽ Заправка 40 BYN
        </DemoButton>
        <DemoButton onClick={() => submitTx("5999", 10, "Wolt")}>
          🏪 Покупка 10 BYN
        </DemoButton>
      </div>
    </div>
  );
}
