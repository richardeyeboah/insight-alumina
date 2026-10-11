"use client";
import { FormEvent, useCallback, useEffect, useState } from "react";
import "./admin.css";
import Link from "next/link";

type Session = { username: string; ai_enabled: boolean };
type Metrics = { totals: { total: number; active: number; cancelled: number; requested: number; upcoming: number }; daily: {day: string; bookings: number}[]; jobs: {state: string; count: number}[]; last_snapshot: {updated_at: string} | null; source: string; timezone: string };
type Booking = {uid: string; event_type_id: number; starts_at: string; ends_at: string; status: string};
type Job = {id: number; kind: string; state: string; attempts: number; last_error: string | null};
type Summary = {summary: string; model: string; created_at: string} | null;
async function api<T>(path: string, body?: object): Promise<T> {
 const res = await fetch(`/api/admin/${path}`, {method: body ? "POST" : "GET", headers: body ? {"Content-Type":"application/json"} : {}, body: body ? JSON.stringify(body) : undefined, cache:"no-store"});
 const data = await res.json(); if (!res.ok) throw new Error(data.detail || "Unable to load administration"); return data;
}

export default function Admin() {
 const [session,setSession]=useState<Session|null>(null); const [loading,setLoading]=useState(true); const [busy,setBusy]=useState(false);
 const [error,setError]=useState(""); const [notice,setNotice]=useState(""); const [metrics,setMetrics]=useState<Metrics|null>(null);
 const [bookings,setBookings]=useState<Booking[]>([]); const [jobs,setJobs]=useState<Job[]>([]); const [summary,setSummary]=useState<Summary>(null);
 const [tab,setTab]=useState("overview");
 const load=useCallback(async()=>{
  const current=await api<Session>("session"); setSession(current);
  const [m,b,j,s]=await Promise.all([api<Metrics>("metrics"),api<{bookings:Booking[]}>("bookings"),api<{jobs:Job[]}>("jobs"),api<{summary:Summary}>("summary")]);
  setMetrics(m);setBookings(b.bookings);setJobs(j.jobs);setSummary(s.summary);
 },[]);
 useEffect(()=>{Promise.resolve().then(load).catch(e=>{if(e.message!=="Sign in required" && e.message!=="Session expired")setError(e.message)}).finally(()=>setLoading(false));},[load]);
 async function login(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();setBusy(true);setError("");const form=new FormData(event.currentTarget);
  try{await api("login",{username:form.get("username"),password:form.get("password")});await load();}catch(e){setError((e as Error).message)}finally{setBusy(false)}
 }
 async function action(path:string,message:string){setBusy(true);setError("");setNotice("");try{await api(path,{});setNotice(message);await load()}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 async function logout(){try{await api("logout",{});setSession(null);setMetrics(null);setBookings([]);setJobs([]);setSummary(null);setNotice("")}catch(e){setError((e as Error).message)}}
 const date=(s:string)=>new Date(s).toLocaleString(undefined,{dateStyle:"medium",timeStyle:"short"});
 return <main className="admin-shell"><header className="admin-header"><Link href="/">✳ insight alumina</Link><span>STUDIO ADMINISTRATION</span>{session && <button onClick={logout}>Sign out</button>}</header>
  {loading ? <p role="status">Checking your session…</p> : !session ? <section className="admin-login"><p className="eyebrow">PRIVATE WORKSPACE</p><h1>Welcome back.</h1><p>Sign in to manage booking insights and background processing.</p><form onSubmit={login}><label>Username<input name="username" autoComplete="username" required maxLength={100}/></label><label>Password<input name="password" type="password" autoComplete="current-password" required maxLength={1024}/></label><button className="admin-primary" disabled={busy}>{busy?"Signing in…":"Sign in"}</button></form><p className="admin-caption">Administrator accounts are provisioned on the server. There is no public registration.</p>{error&&<p className="admin-error" role="alert">{error}</p>}</section> : <>
  <div className="admin-title"><div><p className="eyebrow">YOUR STUDIO, AT A GLANCE</p><h1>Clearer perspective.</h1><p>Signed in as {session.username}. Data comes from received booking events.</p></div><button disabled={busy} onClick={()=>{setBusy(true);load().catch(e=>setError(e.message)).finally(()=>setBusy(false))}}>Refresh data ↻</button></div>
  <nav className="admin-tabs" aria-label="Administration sections">{["overview","bookings","jobs","insights"].map(t=><button key={t} aria-current={tab===t?"page":undefined} onClick={()=>setTab(t)}>{t}</button>)}</nav>
  {error&&<p className="admin-error" role="alert">{error}</p>}{notice&&<p className="admin-notice" role="status">{notice}</p>}
  {tab==="overview" && <>{metrics ? <><div className="metric-grid">{[["Recorded bookings",metrics.totals.total],["Active",metrics.totals.active],["Upcoming",metrics.totals.upcoming],["Cancelled",metrics.totals.cancelled]].map(([label,value])=><article key={label}><p>{label}</p><strong>{value}</strong></article>)}</div><section className="admin-panel"><h2>Appointments over the last 30 days</h2><p className="admin-caption">By appointment date, in UTC. Counts include cancelled appointments.</p>{metrics.daily.length ? <div className="admin-chart">{metrics.daily.map(d=><div key={d.day}><span>{d.day}</span><div className="chart-track"><div style={{width:`${d.bookings/Math.max(...metrics.daily.map(x=>x.bookings))*100}%`}}/></div><strong>{d.bookings}</strong></div>)}</div> : <p className="empty">No booking events recorded for this period.</p>}</section><section className="admin-panel"><h2>Processing status</h2><div className="job-counts">{metrics.jobs.map(j=><span key={j.state}>{j.count} {j.state}</span>)}</div><p className="admin-caption">Last worker snapshot: {metrics.last_snapshot ? date(metrics.last_snapshot.updated_at) : "No snapshot yet"}</p></section><p className="admin-caption">{metrics.source}. No revenue is inferred.</p></> : <p>No metrics loaded. Refresh to try again.</p>}</>}
  {tab==="bookings" && <section className="admin-panel"><h2>Recent booking records</h2><p className="admin-caption">Latest 100 records. Manage appointment changes in Cal.com. Personal attendee information is not stored here.</p><div className="admin-table-scroll"><table><thead><tr><th>Booking</th><th>Event type</th><th>Appointment</th><th>Status</th></tr></thead><tbody>{bookings.map(b=><tr key={b.uid}><td>{b.uid}</td><td>{b.event_type_id}</td><td>{date(b.starts_at)}</td><td><span className={`status ${b.status}`}>{b.status}</span></td></tr>)}</tbody></table></div>{!bookings.length&&<p className="empty">Your received booking records will appear here.</p>}</section>}
  {tab==="jobs" && <section className="admin-panel"><h2>Background jobs</h2><p className="admin-caption">Latest 50 jobs. Failed jobs can be retried after their cause is resolved.</p>{jobs.length ? jobs.map(j=><article className="admin-job" key={j.id}><div><strong>#{j.id} · {j.kind.replaceAll("_"," ")}</strong><p>{j.state} · {j.attempts} attempts</p>{j.last_error&&<p>{j.last_error}</p>}</div>{j.state==="failed"&&<button disabled={busy} onClick={()=>action(`jobs/${j.id}/retry`,"Job queued for retry.")}>Retry job</button>}</article>) : <p className="empty">No background jobs yet.</p>}</section>}
  {tab==="insights" && <section className="admin-panel"><p className="eyebrow">OPTIONAL AI</p><h2>Business reflection</h2><p>Summaries use aggregate booking counts only. They do not see customer details or reading notes, and can be inaccurate.</p><button className="admin-primary" disabled={busy||!session.ai_enabled} onClick={()=>action("summary","Today’s summary job is queued. Refresh after the worker finishes.")}>{session.ai_enabled?"Request today’s summary":"AI is disabled"}</button><p className="admin-caption">At most one new summary job per UTC day. Refresh to see completed results.</p>{summary ? <div className="ai-result"><p>{summary.summary}</p><small>Generated by {summary.model} · {date(summary.created_at)} · Review before acting.</small></div> : <p className="empty">No generated summary yet.</p>}</section>}
  </>}
 </main>;
}
