// filepath: frontend/src/App.jsx
import GameMap from "./components/GameMap";
import DemoPanel from "./components/DemoPanel";
import NotificationToast from "./components/NotificationToast";
import { useGameState } from "./hooks/useGameState";

export default function App() {
  const { hexes, stats, activeQuest, achievements, notification, submitTx } = useGameState();

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "#0d0d1a",
      }}
    >
      <div style={{ flex: 1, position: "relative" }}>
        <GameMap hexes={hexes} />
        <NotificationToast notification={notification} />
      </div>
      <DemoPanel
        stats={stats}
        activeQuest={activeQuest}
        achievements={achievements}
        submitTx={submitTx}
      />
    </div>
  );
}
