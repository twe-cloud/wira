import { AnimatePresence, motion } from "motion/react";
import { type ReactNode, useEffect, useRef, useState } from "react";

type Turn = {
  from: "owner" | "agent";
  text: string;
  time: string;
  pause?: number;
  ticks?: "sent" | "delivered" | "read";
};

const CONTACT = {
  name: "Wira",
  number: "+1 (945) 555-0147",
  status: "online",
  avatar: `${import.meta.env.BASE_URL}wira-logo.png`,
};

const TURNS: Turn[] = [
  { from: "owner", text: "Sasa Wira, leo niko na mambo mingi 😅", time: "9:41 AM", pause: 1500, ticks: "read" },
  { from: "agent", text: "Niko hapa boss 🙂 Tuanzie wapi — orders, stock, ama follow-up?", time: "9:41 AM" },
  { from: "owner", text: "Kuna customer ameuliza catering ya watu 40 for Saturday. Anataka quote haraka before lunch.", time: "9:42 AM", pause: 1650, ticks: "read" },
  { from: "agent", text: "Sawa. Nakuandikia warm reply sai: “Hi — yes, we can do that for 40. Do you want pickup or delivery, and should I include jollof + two proteins?”", time: "9:42 AM" },
  { from: "owner", text: "Hiyo ni safi 👌 Make it sound sharp, si too formal.", time: "9:43 AM", pause: 1450, ticks: "read" },
  { from: "agent", text: "Done. Pia nimeona two unread WhatsApp leads za Friday pickup. Nikudraftie one reply utumie wote?", time: "9:43 AM" },
  { from: "owner", text: "Wĩ mwega? Yes, hiyo ndio nataka. One clean reply niforward tu.", time: "9:44 AM", pause: 1600, ticks: "read" },
  { from: "agent", text: "Nĩ wega 😄 Draft hii: “Yes, Friday pickup is open after 4. Send me your order and I’ll confirm timing.” Short, clear, no long story.", time: "9:44 AM" },
  { from: "owner", text: "Ber? Kuna supplier wa drinks aliconfirm ama bado anapotea?", time: "11:18 AM", pause: 1550, ticks: "read" },
  { from: "agent", text: "Bado hajaconfirm. Nimekuwekea follow-up ya hio: “Just checking before I lock today’s prep — are we confirmed on the drinks order?”", time: "11:19 AM" },
  { from: "owner", text: "Mwari, hiyo poster ya weekend offer iko live ama bado old date?", time: "1:06 PM", pause: 1600, ticks: "read" },
  { from: "agent", text: "Bado old date. Nimeflag hiyo as urgent because inaweza kuconfuse customers. Nikutengenezee new copy ya haraka?", time: "1:06 PM" },
  { from: "owner", text: "Eeh bana 😂 And keep the vibe playful kidogo, si corporate flyer energy.", time: "1:07 PM", pause: 1450, ticks: "read" },
  { from: "agent", text: "Got you. “This weekend tunapika proper — place your tray orders mapema.” Clean, local, and still premium ✨", time: "1:07 PM" },
  { from: "owner", text: "Supa. Kuna customer amesema delivery imechelewa and anaonekana kukasirika.", time: "4:32 PM", pause: 1550, ticks: "read" },
  { from: "agent", text: "Nimekuandikia apology yenye haisound defensive: “Sorry — your order is on the way and I should have updated you earlier. I’ll send the exact ETA in a minute.”", time: "4:33 PM" },
  { from: "owner", text: "Mora? Hiyo ETA iko?", time: "4:34 PM", pause: 1450, ticks: "read" },
  { from: "agent", text: "Yes — driver ako minutes 12 away. Nimeweka location pin ready pia ukiamua kuituma 📍", time: "4:34 PM" },
  { from: "owner", text: "Nice. Jioni nikumbushe mwenye hakujibu quote asipotee tu hivyo.", time: "7:08 PM", pause: 1500, ticks: "read" },
  { from: "agent", text: "Already lined up. Nitakusortia a gentle nudge around 7:30: “Just checking in before I close the evening — should I still hold that quote for you?”", time: "7:08 PM" },
  { from: "owner", text: "Perfect 🙌 Hii ndio help nilikuwa nataka — inashika context yote bila kunifanya nirudie kila kitu.", time: "7:09 PM", pause: 1500, ticks: "read" },
  { from: "agent", text: "Exactly. Unaongea vile unaongea kawaida, mimi nashika thread, tone, na task hadi ikae sorted.", time: "7:09 PM" },
];

const EASE = [0.22, 1, 0.36, 1] as const;

function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const m = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(m.matches);
    const onChange = () => setReduced(m.matches);
    m.addEventListener?.("change", onChange);
    return () => m.removeEventListener?.("change", onChange);
  }, []);
  return reduced;
}

function Icon({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-black/8 bg-white/70 text-[#54656f] shadow-[0_1px_0_rgba(0,0,0,0.04)]">
      {children}
    </span>
  );
}

function MessageTicks({ state = "read" }: { state?: Turn["ticks"] }) {
  const color = state === "read" ? "text-[#53bdeb]" : "text-[#8696a0]";
  return <span className={`ml-1 inline-flex text-[10px] leading-none ${color}`}>✓✓</span>;
}

export default function PhoneMockup() {
  const reduced = useReducedMotion();
  const [turnIdx, setTurnIdx] = useState(0);
  const [typing, setTyping] = useState(false);
  const listRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (reduced) return;
    const turn = TURNS[turnIdx];

    if (!turn) {
      const id = setTimeout(() => {
        setTurnIdx(0);
        setTyping(false);
      }, 3600);
      return () => clearTimeout(id);
    }

    if (turn.from === "agent") {
      setTyping(true);
      const id = setTimeout(() => {
        setTyping(false);
        setTurnIdx((i) => i + 1);
      }, turn.pause ?? 1450 + Math.min(3200, turn.text.length * 18));
      return () => clearTimeout(id);
    }

    const id = setTimeout(() => setTurnIdx((i) => i + 1), turn.pause ?? 1350);
    return () => clearTimeout(id);
  }, [turnIdx, reduced]);

  const visibleTurns = reduced ? TURNS : TURNS.slice(0, turnIdx);

  useEffect(() => {
    const el = listRef.current;
    if (!el) return;
    const top = el.scrollHeight;
    el.scrollTo({ top, behavior: reduced ? "auto" : "smooth" });
  }, [visibleTurns.length, typing, reduced]);

  return (
    <div
      className="relative mx-auto"
      style={{ width: 336, maxWidth: "100%" }}
      aria-label="Animated WhatsApp-style example showing a smooth, multilingual chat between an owner and Wira."
    >
      <div className="rounded-[44px] bg-[#111b21] p-3 shadow-2xl" style={{ boxShadow: "0 34px 80px -24px rgba(14,20,19,.42)" }}>
        <div className="overflow-hidden rounded-[34px] bg-[#efeae2]" style={{ height: 620 }}>
          <div className="flex items-center justify-between bg-[#0b141a] px-5 pt-3 pb-1 text-[11px] text-white/92">
            <span>9:41</span>
            <div className="flex items-center gap-1.5">
              <span className="inline-block h-1.5 w-3 rounded-sm bg-white/70" />
              <span className="inline-block h-1.5 w-3 rounded-sm bg-white/70" />
              <span className="inline-block h-2.5 w-5 rounded-sm border border-white/70" />
            </div>
          </div>

          <div className="flex items-center gap-3 bg-[#075e54] px-4 py-3 text-white">
            <img
              src={CONTACT.avatar}
              alt="Wira logo"
              className="h-10 w-10 rounded-full object-cover ring-1 ring-white/20"
            />
            <div className="min-w-0 flex-1">
              <div className="truncate text-[15px] font-medium leading-tight">{CONTACT.name}</div>
              <div className="truncate text-[11px] text-white/78">{CONTACT.number} · {CONTACT.status}</div>
            </div>
            <div className="flex items-center gap-2 text-white/88">
              <span aria-hidden>⌕</span>
              <span aria-hidden>◌</span>
              <span aria-hidden>⋮</span>
            </div>
          </div>

          <div
            ref={listRef}
            className="flex flex-col gap-2 overflow-hidden px-3 py-3"
            style={{
              height: 536,
              background: "linear-gradient(180deg, rgba(255,255,255,0.28), rgba(255,255,255,0.16)), #efeae2",
            }}
          >
            <div className="self-center max-w-[88%] rounded-2xl bg-[#f7f5f2] px-3 py-1.5 text-center text-[10px] leading-tight text-[#667781] shadow-[0_1px_1px_rgba(0,0,0,0.06)]">
              Messages and calls are end-to-end encrypted. No one outside this chat can read or listen.
            </div>

            <AnimatePresence initial={false} mode="popLayout">
              {visibleTurns.map((turn, i) => {
                const owner = turn.from === "owner";
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10, scale: 0.985 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.28, ease: EASE }}
                    className={owner ? "self-end items-end" : "self-start items-start"}
                  >
                    <div
                      className={owner ? "max-w-[82%] rounded-[18px] rounded-br-[6px] bg-[#d9fdd3] px-3 py-2.5 text-[13px] leading-[1.35] text-[#111b21] shadow-[0_1px_1px_rgba(0,0,0,0.06)]" : "max-w-[84%] rounded-[18px] rounded-bl-[6px] border border-black/5 bg-white px-3 py-2.5 text-[13px] leading-[1.35] text-[#111b21] shadow-[0_1px_1px_rgba(0,0,0,0.08)]"}
                    >
                      {turn.text}
                    </div>
                    <div className={owner ? "mt-1 flex items-center pr-1 text-[10px] text-[#667781]" : "mt-1 pl-1 text-[10px] text-[#667781]"}>
                      {turn.time}
                      {owner && <MessageTicks state={turn.ticks} />}
                    </div>
                  </motion.div>
                );
              })}

              {typing && (
                <motion.div
                  key="typing"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="self-start"
                >
                  <div className="flex items-center gap-1 rounded-[18px] rounded-bl-[6px] border border-black/5 bg-white px-3 py-2.5 shadow-[0_1px_1px_rgba(0,0,0,0.08)]">
                    {[0, 1, 2].map((d) => (
                      <motion.span
                        key={d}
                        className="inline-block h-1.5 w-1.5 rounded-full bg-[#667781]"
                        animate={{ y: [0, -3, 0] }}
                        transition={{ duration: 0.9, repeat: Infinity, delay: d * 0.15, ease: "easeInOut" }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="border-t border-black/6 bg-[#f0f2f5] px-3 py-2.5">
            <div className="flex items-center gap-2">
              <Icon>＋</Icon>
              <div className="flex-1 rounded-full bg-white px-4 py-2 text-[13px] text-[#8696a0] shadow-[inset_0_0_0_1px_rgba(0,0,0,0.04)]">
                Message
              </div>
              <Icon>📎</Icon>
              <Icon>🎤</Icon>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
