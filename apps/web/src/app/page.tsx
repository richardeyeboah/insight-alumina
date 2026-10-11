function bookingUrl(): string | null {
  const value = process.env.NEXT_PUBLIC_CAL_BOOKING_URL;
  if (!value) return null;
  try {
    const url = new URL(value);
    return url.protocol === "https:" && url.hostname === "cal.com" && !url.username && !url.password && url.pathname.split("/").filter(Boolean).length >= 2 ? url.href : null;
  } catch { return null; }
}

export default function Home() {
  const url = bookingUrl();
  return (
    <main className="mx-auto max-w-3xl px-6 py-20 sm:py-28">
      <p className="text-sm uppercase tracking-[0.25em] text-purple-300">Insight Alumina</p>
      <h1 className="mt-6 text-4xl font-semibold leading-tight sm:text-6xl">Make space for reflection.</h1>
      <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">Explore tarot as a thoughtful moment for perspective and personal reflection.</p>
      <section aria-labelledby="booking" className="mt-12 rounded-2xl border border-purple-300/20 bg-white/5 p-8">
        <h2 id="booking" className="text-2xl font-semibold">Book a tarot reading</h2>
        <p className="mt-4 leading-7 text-slate-300">See available appointments and confirmed session details on our scheduling page.</p>
        {url ? <a href={url} className="mt-6 inline-block rounded-lg bg-purple-200 px-6 py-3 font-semibold text-purple-950 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-purple-200">View availability on Cal.com</a>
          : <p role="status" className="mt-6 text-purple-200">Online booking is being prepared. Please check back soon.</p>}
      </section>
      <p className="mt-8 text-sm leading-6 text-slate-400">Tarot readings are for reflection and entertainment. They do not replace medical, legal, or financial advice.</p>
    </main>
  );
}
