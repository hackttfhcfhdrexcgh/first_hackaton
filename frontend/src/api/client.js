// filepath: frontend/src/api/client.js
import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const api = axios.create({ baseURL, timeout: 10000 });

export const PLAYER_ID = "demo_player_001";

export async function fetchHexes() {
  const res = await api.get("/api/hexes");
  return res.data;
}

export async function submitTransaction(mcc, amount, merchantName) {
  const res = await api.post("/api/transaction", {
    player_id: PLAYER_ID,
    merchant_name: merchantName,
    mcc_code: mcc,
    amount: Number(amount),
    currency: "BYN",
    timestamp: new Date().toISOString(),
  });
  return res.data;
}

export async function fetchProfile() {
  const res = await api.get(`/api/player/${PLAYER_ID}/profile`);
  return res.data;
}

export default api;
