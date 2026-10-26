/* Browser-side on-demand search. Requires a public Ticketmaster Discovery API key in config.js. */
window.searchLiveDMVEvents = async function(apiKey) {
  if (!apiKey) throw new Error("Live search needs a Ticketmaster public API key.");
  const today = new Date();
  const local = new Date(today.toLocaleString("en-US",{timeZone:"America/New_York"}));
  const monday = new Date(local.getFullYear(),local.getMonth(),local.getDate()-((local.getDay()+6)%7));
  const sunday = new Date(monday); sunday.setDate(monday.getDate()+6);
  const iso=d=>[d.getFullYear(),String(d.getMonth()+1).padStart(2,"0"),String(d.getDate()).padStart(2,"0")].join("-");
  const start=iso(monday), end=iso(sunday);
  const validVA=new Set(["arlington","alexandria","tysons","vienna","fairfax","falls church","reston","mclean","herndon","ashburn","dulles"]);
  const validMD=new Set(["national harbor","oxon hill","bethesda","silver spring","rockville","college park","hyattsville","bowie","gaithersburg"]);
  const all=new Map();
  for(const state of ["DC","VA","MD"]){
    for(let page=0;page<3;page++){
      const q=new URLSearchParams({apikey:apiKey,stateCode:state,startDateTime:start+"T00:00:00Z",endDateTime:iso(new Date(sunday.getFullYear(),sunday.getMonth(),sunday.getDate()+1))+"T23:59:59Z",size:"200",page:String(page),sort:"date,asc"});
      const res=await fetch("https://app.ticketmaster.com/discovery/v2/events.json?"+q);
      if(!res.ok) throw new Error("Event provider returned HTTP "+res.status);
      const data=await res.json();
      for(const e of data._embedded?.events||[]) all.set(e.id,e);
      if(page+1 >= (data.page?.totalPages||0)) break;
    }
  }
  const days=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  const events=[];
  for(const e of all.values()){
    const v=e._embedded?.venues?.[0]||{};
    const city=(v.city?.name||"").toLowerCase(),state=v.state?.stateCode||"DC";
    if(state==="VA"&&!validVA.has(city)||state==="MD"&&!validMD.has(city)) continue;
    const date=e.dates?.start?.localDate;
    if(!date||date<start||date>end) continue;
    const seg=(e.classifications?.[0]?.segment?.name||"").toLowerCase();
    const type=seg.includes("sport")?"sport":seg.includes("music")?"concert":"expo";
    const raw=e.dates?.start?.localTime;
    let time="Time TBA";
    if(raw){const parts=raw.split(":");const h=Number(parts[0]);time=(h%12||12)+":"+parts[1]+" "+(h>=12?"PM":"AM");}
    events.push({id:"tm-"+e.id,day:days[new Date(date+"T12:00:00").getDay()],date,time,
      name:e.name||"Event",address:[v.address?.line1,v.city?.name,state].filter(Boolean).join(", ")||v.name||"Venue TBA",
      pickup:"End time unconfirmed; check event listing",rating:type==="expo"?3:4,type,
      profile:"Demand estimate only",tag:type[0].toUpperCase()+type.slice(1),
      status:e.dates?.status?.code||"onsale",source:e.url||""});
  }
  events.sort((a,b)=>a.date.localeCompare(b.date)||a.time.localeCompare(b.time));
  if(!events.length) throw new Error("No events found; keeping saved schedule.");
  return {week_label:start+" – "+end,generated_at:new Date().toISOString(),
    region:"DC • Northern Virginia • Maryland",source:"Ticketmaster Discovery API",events};
};
