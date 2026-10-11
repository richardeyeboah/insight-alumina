"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

const Cal = dynamic(() => import("@calcom/embed-react"), { ssr: false, loading: () => <p className="booking-loading" role="status">Loading available readings…</p> });

function Arrow() { return <span aria-hidden="true">↗</span>; }
function TarotCard({ type, className = "" }: { type: "sun" | "moon" | "star"; className?: string }) {
  return <div className={`tarot-card ${className}`} aria-hidden="true">
    <svg viewBox="0 0 240 390" fill="none">
      <rect x="13" y="13" width="214" height="364" rx="95" stroke="currentColor" strokeWidth="1" />
      <rect x="21" y="21" width="198" height="348" rx="88" stroke="currentColor" strokeOpacity=".4" />
      <path d="M38 290Q120 235 202 290M38 299Q120 254 202 299M42 310Q120 276 198 310" stroke="currentColor" />
      {type === "sun" ? <><circle cx="120" cy="153" r="42" stroke="currentColor" /><circle cx="120" cy="153" r="35" stroke="currentColor" strokeOpacity=".5" />{Array.from({length:16}, (_,i)=><path key={i} d="M120 94V72" stroke="currentColor" transform={`rotate(${i*22.5} 120 153)`} />)}<path d="M108 148h3m19 0h3m-22 17q9 7 18 0" stroke="currentColor" strokeLinecap="round" /></> : type === "moon" ? <><path d="M140 92c-60-9-91 63-47 105 22 21 58 22 81 2-47 0-66-70-34-107Z" stroke="currentColor" /><path d="m74 102 3-8 3 8 8 3-8 3-3 8-3-8-8-3Zm92 51 3-8 3 8 8 3-8 3-3 8-3-8-8-3Z" stroke="currentColor" /></> : <><path d="m120 86 10 49 39-28-27 40 48 10-48 10 27 40-39-28-10 49-10-49-39 28 27-40-48-10 48-10-27-40 39 28Z" stroke="currentColor" /><circle cx="120" cy="157" r="13" stroke="currentColor" /></>}
      <path d="M72 270q-15-26-5-48 23 12 22 34m79 14q15-26 5-48-23 12-22 34M85 267l-15-31m85 31 15-31" stroke="currentColor" />
      <text x="120" y="54" textAnchor="middle" fill="currentColor" stroke="none" fontSize="12" letterSpacing="3">{type === "sun" ? "XIX" : type === "moon" ? "XVIII" : "XVII"}</text>
      <text x="120" y="340" textAnchor="middle" fill="currentColor" stroke="none" fontSize="16" letterSpacing="3">THE {type.toUpperCase()}</text>
    </svg>
  </div>;
}
const questions = [
  ["Do I need to know anything about tarot?", "No prior knowledge is needed. You can arrive with a question, a theme you would like to reflect on, or simply curiosity."],
  ["Can a reading tell me what will happen?", "Think of tarot as a way to explore perspective, rather than a guarantee of a future outcome. Your decisions remain your own."],
  ["Where can I find session details and pricing?", "The booking section below lists the available options. Select a session to review its details and choose an appointment time without leaving this website."],
  ["How do I reschedule or cancel?", "For a Cal.com booking, use the links in your confirmation email. Check the published cancellation and rescheduling terms before confirming your appointment."],
];

export default function Studio({booking}: {booking: string | null}) {
  const [menu, setMenu] = useState(false);
  const [open, setOpen] = useState<number | null>(0);
  const [selected, setSelected] = useState<number | null>(null);
  const reflections = ["What deserves more of your attention?", "What could you give yourself permission to release?", "Where is there room for a new perspective?"];
  return <>
    <a className="skip" href="#main">Skip to content</a>
    <header className="header">
      <a className="brand" href="#" aria-label="Insight Alumina home"><span className="brand-mark" aria-hidden="true">✳</span><span>insight alumina<span className="brand-sub">TAROT & REFLECTION</span></span></a>
      <button className="menu-toggle" aria-label={menu ? "Close menu" : "Open menu"} aria-expanded={menu} aria-controls="navigation" onClick={()=>setMenu(!menu)}>{menu ? "Close −" : "Menu +"}</button>
      <nav id="navigation" className={menu ? "nav is-open" : "nav"} aria-label="Main navigation">
        <a href="#approach" onClick={()=>setMenu(false)}>The approach</a><a href="#experience" onClick={()=>setMenu(false)}>Your reading</a><a href="#questions" onClick={()=>setMenu(false)}>Questions</a><a className="nav-book" href="#book" onClick={()=>setMenu(false)}>Book a reading <Arrow /></a>
      </nav>
    </header>
    <main id="main">
      <section className="hero">
        <div className="hero-copy"><p className="eyebrow"><span className="tiny-star">✦</span> A LITTLE STILLNESS. A DIFFERENT PERSPECTIVE.</p>
          <h1>The answers begin<br/>with a <em>pause.</em></h1>
          <p className="intro">A space to step out of the noise, explore what’s on your mind, and see your story in a different light.</p>
          <div className="hero-actions"><a href="#book" className="button">Find your moment <Arrow /></a><a href="#approach" className="text-link">Explore the approach <span aria-hidden="true">↓</span></a></div>
          <p className="hero-note">TAROT FOR REFLECTION. ROOM FOR POSSIBILITY.</p>
        </div>
        <div className="hero-art"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><span className="art-star star-one">✧</span><span className="art-star star-two">✦</span><span className="art-dot"/><TarotCard type="moon" className="card-moon"/><TarotCard type="sun" className="card-sun"/><div className="art-caption"><span>01 / A NEW PERSPECTIVE</span><span>INSIGHT ALUMINA</span></div></div>
      </section>
      <div className="interlude"><span>A practice of perspective</span><span aria-hidden="true">✳</span><span>Not a fixed prediction</span><span aria-hidden="true">✳</span><span>Your story. Your choices.</span></div>
      <section id="approach" className="approach section-wrap">
        <div><p className="eyebrow">01 — THE APPROACH</p><h2>A mirror,<br/><em>not a map.</em></h2></div>
        <div className="approach-copy"><p className="large-copy">Sometimes, a different way of looking is all it takes to make space for something new.</p><p>Tarot offers a visual language for reflection. The cards invite questions, connections, and possibilities — without making your decisions for you.</p><p>Bring a question. Bring an open mind. Leave room for your own interpretation.</p><a href="#experience" className="text-link">What a reading can look like <Arrow /></a></div>
      </section>
      <section id="experience" className="experience section-wrap">
        <div className="section-top"><div><p className="eyebrow">02 — YOUR READING</p><h2>A moment that’s<br/><em>yours to explore.</em></h2></div><p>You don’t need a perfect question.<br/>Just a place to begin.</p></div>
        <div className="steps">
          <article><span className="step-number">01</span><h3>Arrive as you are.</h3><p>Consider what’s on your mind. A change, a decision, a recurring thought — or no particular question at all.</p></article>
          <article><span className="step-number">02</span><h3>Make room for insight.</h3><p>Use the imagery and themes of tarot to reflect on possibilities and notice what resonates with you.</p></article>
          <article><span className="step-number">03</span><h3>Carry it your way.</h3><p>Take the questions that feel useful. Give yourself time to consider them, with your own judgment at the center.</p></article>
        </div>
        <p className="experience-note">Explore the session details and choose an appointment in the booking section below.</p>
      </section>
      <section className="reflection section-wrap" aria-labelledby="reflection-title"><div className="reflection-copy"><p className="eyebrow">A SMALL MOMENT, RIGHT HERE</p><h2 id="reflection-title">Follow your<br/><em>curiosity.</em></h2><p>Choose a card for a question to sit with.<br/>No prediction. Just a little perspective.</p><div className="reflection-result" aria-live="polite">{selected === null ? <span>Which one catches your eye?</span> : <><span className="eyebrow">YOUR REFLECTION</span><p>{reflections[selected]}</p><button className="reset" onClick={()=>setSelected(null)}>Choose again ↺</button></>}</div></div><div className="reflection-cards">{(["star", "moon", "sun"] as const).map((type,i)=><button key={type} className={`choose-card ${selected === i ? "chosen" : ""}`} onClick={()=>setSelected(i)} aria-label={`Choose ${["the Star","the Moon","the Sun"][i]} reflection card`} aria-pressed={selected === i}><TarotCard type={type}/><span>{["I","II","III"][i]}</span></button>)}</div></section>
      <section id="questions" className="faq section-wrap"><div><p className="eyebrow">03 — A FEW QUESTIONS</p><h2>Before<br/><em>you begin.</em></h2></div><div className="faq-list">{questions.map(([q,a],i)=><div className="faq-item" key={q}><h3><button aria-expanded={open===i} aria-controls={`answer-${i}`} onClick={()=>setOpen(open===i ? null : i)}>{q}<span aria-hidden="true">{open===i ? "−" : "+"}</span></button></h3><div id={`answer-${i}`} hidden={open!==i}><p>{a}</p></div></div>)}</div></section>
      <section id="book" className="booking section-wrap"><span className="booking-star" aria-hidden="true">✳</span><p className="eyebrow">A LITTLE SPACE FOR YOU</p><h2>Let’s see what<br/><em>comes to light.</em></h2><p>Make time for a different perspective.</p>{booking ? <div className="booking-widget"><Cal calLink={new URL(booking).pathname.replace(/^\/+|\/+$/g, "")} config={{ theme: "light" }} style={{ width: "100%", minHeight: "650px", overflow: "auto" }} /><p className="booking-provider">Scheduling securely powered by Cal.com. Choose a session above to continue.</p><details className="booking-fallback"><summary>Having trouble loading the calendar?</summary><p>Check your connection or allow the Cal.com embed in your browser. <a href={booking}>Open the scheduling page ↗</a></p></details></div> : <><span className="booking-status">Online booking is coming soon</span><p className="booking-small">Session details and availability will appear here when scheduling opens.</p></>}<p className="booking-foot">YOUR NEXT CHAPTER IS STILL YOURS TO WRITE.</p></section>
    </main>
    <footer className="footer"><div className="footer-top"><a className="brand" href="#"><span className="brand-mark" aria-hidden="true">✳</span><span>insight alumina<span className="brand-sub">TAROT & REFLECTION</span></span></a><a className="text-link" href="#main">Back to the beginning ↑</a></div><div className="footer-bottom"><span>© 2026 Insight Alumina</span><p>For reflection and entertainment. Tarot does not replace medical, legal, or financial advice.</p></div></footer>
  </>;
}
