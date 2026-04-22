// filepath: frontend/src/hooks/useGameState.js
import { useCallback, useEffect, useState } from "react";
import { fetchHexes, fetchProfile, submitTransaction } from "../api/client";

export function useGameState() {
  const [hexes, setHexes] = useState([]);
  const [stats, setStats] = useState({ total: 37, unlocked: 0, achievements_count: 0 });
  const [activeQuest, setActiveQuest] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [notification, setNotification] = useState({ show: false });

  const refresh = useCallback(async () => {
    try {
      const data = await fetchHexes();
      setHexes(data.hexes || []);
      setStats(data.stats || { total: 37, unlocked: 0, achievements_count: 0 });
      const q = (data.hexes || []).find((h) => h.active_quest);
      setActiveQuest(q ? { ...q.active_quest, hex_id: q.hex_id } : null);
      const profile = await fetchProfile();
      setAchievements(profile.achievements || []);
    } catch (e) {
      console.error("refresh failed", e);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const submitTx = useCallback(async (mcc, amount, merchantName) => {
    try {
      const res = await submitTransaction(mcc, amount, merchantName);

      if (res.hex_unlocked) {
        setHexes((prev) =>
          prev.map((h) =>
            h.hex_id === res.hex_unlocked
              ? { ...h, is_unlocked: true, _justUnlocked: true }
              : h
          )
        );
      }

      setNotification({
        show: true,
        hexUnlocked: res.hex_unlocked,
        reward: res.reward,
        achievements: res.new_achievements || [],
        progress: res.progress,
      });

      setTimeout(() => {
        setNotification({ show: false });
      }, 4000);

      setTimeout(() => {
        refresh();
      }, 800);
    } catch (e) {
      console.error("submitTx failed", e);
      setNotification({
        show: true,
        error: "Ошибка сети",
      });
      setTimeout(() => setNotification({ show: false }), 2500);
    }
  }, [refresh]);

  return { hexes, stats, activeQuest, achievements, notification, submitTx };
}
