import Studio from "./studio";

export default function Home() {
  let booking: string | null = null;
  try {
    const url = new URL(process.env.NEXT_PUBLIC_CAL_BOOKING_URL || "");
    if (url.protocol === "https:" && url.hostname === "cal.com" && !url.username && !url.password && url.pathname.split("/").filter(Boolean).length >= 1) booking = url.href;
  } catch {}
  return <Studio booking={booking} />;
}
