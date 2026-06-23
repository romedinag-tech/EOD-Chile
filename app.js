/* ===================================================================
   EOD Chile · Movilidad Urbana
   Encuestas Origen-Destino · 18 ciudades homologadas y expandidas
   By Rodrigo Medina González · Universidad de Concepción
   =================================================================== */

// ── Constantes de color ──────────────────────────────────────────────────────
const NAVY="#0f2942", NAVY2="#1a4068", OR="#d97706", TEAL="#0891b2",
      GREEN="#16a34a", RED="#dc2626", GREY="#94a3b8", LIME="#65a30d";

const MODO_COL={
  "Público":       NAVY,
  "Privado":       RED,
  "Caminata":      GREEN,
  "Bicicleta":     LIME,
  "No motorizado": GREEN,
  "Combinado":     OR,
  "Otro":          GREY
};
const PROP_COL={
  "Trabajo": NAVY,
  "Estudio": TEAL,
  "Otro":    GREY
};
const QUINTIL_COL=["#d73027","#fc8d59","#fee08b","#91cf60","#1a9850"];
const ETARIO_PAL=["#bdc9e1","#74a9cf","#2b8cbe","#1d6fa4","#145888","#0a3a61"];
const TRAMO_PAL={
  "0-1":"#c7e9c0","1-2":"#a1d99b","2-3":"#74c476",
  "3-4":"#41ab5d","4-5":"#238b45","5-6":"#006d2c","6+":"#00441b"
};
const USUARIO_PAL=["#c6dbef","#6baed6","#2171b5","#084594"];

// ── Coordenadas de ciudades (centroides aproximados) ─────────────────────────
const CITY_COORDS={
  "arica":[-18.478,-70.313],
  "iquique_alto_hospicio":[-20.214,-70.151],
  "copiapo":[-27.366,-70.329],
  "coquimbo_la_serena":[-29.961,-71.346],
  "gran_valparaiso":[-33.046,-71.620],
  "san_antonio":[-33.593,-71.621],
  "gran_santiago":[-33.456,-70.648],
  "rancagua_machali":[-34.170,-70.743],
  "curico":[-34.985,-71.239],
  "talca":[-35.426,-71.665],
  "linares":[-35.846,-71.596],
  "chillan":[-36.608,-72.103],
  "gran_concepcion":[-36.826,-73.049],
  "temuco_padre_las_casas":[-38.735,-72.590],
  "valdivia":[-39.814,-73.246],
  "osorno":[-40.574,-73.136],
  "puerto_montt":[-41.473,-72.941],
  "punta_arenas":[-53.163,-70.907]
};

// ── Estado global ────────────────────────────────────────────────────────────
const S={index:[],data:{},sel:null};
const MAPS=[];
const CH={};
let odMap=null, odLyr=null, odInfo=null, odLegend=null;
let mapView="gen";
let nacMap=null, nacMapLyr=null;
let cmpVar="modal", cmpBuilt=false, cmpIndSel="pct_publico";
let rankInd="pct_publico", rankAsc=false;
let horSeg="total", distSeg="total";
let odPer="all", odTopN=50, odEsc="auto";
const PER_LBL={all:"Día completo",pm:"Punta mañana",pmd:"Punta mediodía",pt:"Punta tarde",fp:"Fuera de punta"};

// ── Utilidades ───────────────────────────────────────────────────────────────
function getJSON(url){
  return fetch(url).then(r=>r.text())
    .then(t=>JSON.parse(t.replace(/\bNaN\b/g,"null").replace(/-?\bInfinity\b/g,"null")));
}

function slugify(s){
  return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"")
    .replace(/[^a-z0-9]+/g,"_").replace(/^_|_$/g,"");
}

function fmt(x,d=1){
  if(x==null||!isFinite(x))return "s/d";
  return x.toLocaleString("es-CL",{minimumFractionDigits:d,maximumFractionDigits:d});
}

function fmtM(x){
  if(x==null||!isFinite(x))return "s/d";
  if(x>=1e6)return fmt(x/1e6,1)+"M";
  if(x>=1e3)return fmt(x/1e3,0)+"k";
  return fmt(x,0);
}

function pct(v){
  if(v==null||!isFinite(v))return "s/d";
  return fmt(v,1)+"%";
}

// ── Colores de período horario ───────────────────────────────────────────────
function horaColor(h){
  if(h>=7&&h<9)   return "rgba(15,41,66,.88)";
  if(h>=12&&h<14) return "rgba(217,119,6,.85)";
  if(h>=17&&h<20) return "rgba(8,145,178,.82)";
  return "rgba(148,163,184,.4)";
}

// ── Tema claro / oscuro ──────────────────────────────────────────────────────
const CARTO_LIGHT="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
const CARTO_DARK ="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

function isDark(){return document.documentElement.classList.contains("dark");}

function applyMapTheme(){
  const u=isDark()?CARTO_DARK:CARTO_LIGHT;
  MAPS.forEach(m=>{try{m.carto.setUrl(u);}catch(e){}});
}

function applyChartTheme(){
  if(!window.Chart)return;
  Chart.defaults.color      =isDark()?"#8b949e":"#64748b";
  Chart.defaults.borderColor=isDark()?"rgba(48,54,61,.8)":"rgba(15,23,42,.05)";
}

function rerenderActive(){
  const t=currentTab();
  if(S.sel){
    if(t==="resumen")    renderResumen(S.sel);
    if(t==="movilidad")  renderMovilidad(S.sel);
    if(t==="demografia") renderDemografia(S.sel);
    if(t==="ingreso")    renderIngreso(S.sel);
    if(t==="mapas")      drawMapView(S.sel);
  }
  if(t==="nacional")   renderNacional();
  if(t==="comparador") renderComparador();
}

function setTheme(dark){
  document.documentElement.classList.toggle("dark",dark);
  try{localStorage.setItem("theme",dark?"dark":"light");}catch(e){}
  updateThemeIcon();
  applyChartTheme();
  applyMapTheme();
  rerenderActive();
}

const MOON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>';
const SUN ='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
function updateThemeIcon(){const b=document.getElementById("themeToggle");if(b)b.innerHTML=isDark()?SUN:MOON;}

// ── Mapa Leaflet — helpers ───────────────────────────────────────────────────
function authorWM(map){
  const c=L.control({position:"bottomleft"});
  c.onAdd=function(){const d=L.DomUtil.create("div","author-wm");d.textContent="By Rodrigo Medina G.";return d;};
  c.addTo(map);return c;
}

function mapChrome(map){
  const claro=L.tileLayer(isDark()?CARTO_DARK:CARTO_LIGHT,
    {attribution:'&copy; OpenStreetMap &copy; CARTO',maxZoom:19});
  const sat=L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {attribution:'Imagery &copy; Esri, Maxar, Earthstar Geographics',maxZoom:19});
  claro.addTo(map);MAPS.push({map,carto:claro});
  L.control.layers({"Mapa":claro,"Satélite":sat},null,{position:"topright"}).addTo(map);
  const fc=L.control({position:"topleft"});
  fc.onAdd=function(){
    const d=L.DomUtil.create("div","leaflet-bar fs-ctrl");
    const a=L.DomUtil.create("a","",d);
    a.href="#";a.title="Pantalla completa";a.setAttribute("role","button");a.setAttribute("aria-label","Pantalla completa");
    a.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3m13-5v3a2 2 0 1-2 2h-3"/></svg>';
    L.DomEvent.on(a,"click",function(e){
      L.DomEvent.stop(e);const el=map.getContainer();
      if(!document.fullscreenElement)(el.requestFullscreen||el.webkitRequestFullscreen||function(){}).call(el);
      else(document.exitFullscreen||document.webkitExitFullscreen||function(){}).call(document);
      setTimeout(()=>map.invalidateSize(),250);
    });
    return d;
  };
  fc.addTo(map);authorWM(map);
  return{claro,sat};
}

// ── Tabs ─────────────────────────────────────────────────────────────────────
function currentTab(){
  const b=document.querySelector(".tabs button.on");return b?b.dataset.tab:"resumen";
}

function activateTab(t){
  document.querySelectorAll(".tabs button").forEach(x=>{
    const on=x.dataset.tab===t;
    x.classList.toggle("on",on);x.setAttribute("aria-selected",on?"true":"false");
  });
  document.querySelectorAll(".panel").forEach(p=>p.classList.toggle("on",p.id==="p-"+t));
  if(t==="mapas"&&odMap)setTimeout(()=>odMap.invalidateSize(),60);
  if(t==="resumen"&&S.sel)    renderResumen(S.sel);
  if(t==="movilidad"&&S.sel)  renderMovilidad(S.sel);
  if(t==="demografia"&&S.sel) renderDemografia(S.sel);
  if(t==="ingreso"&&S.sel)    renderIngreso(S.sel);
  if(t==="mapas"&&S.sel)      renderMapas(S.sel);
  if(t==="nacional")          renderNacional();
  if(t==="comparador")        renderComparador();
  writeURL();
}

document.querySelectorAll(".tabs button").forEach(b=>b.onclick=()=>activateTab(b.dataset.tab));

(function(){
  const nav=document.querySelector(".tabs");if(!nav)return;
  const btns=[...nav.querySelectorAll("button")];
  nav.addEventListener("keydown",e=>{
    if(e.key!=="ArrowRight"&&e.key!=="ArrowLeft")return;
    const i=btns.indexOf(document.activeElement);if(i<0)return;
    e.preventDefault();
    const n=(i+(e.key==="ArrowRight"?1:btns.length-1)+btns.length)%btns.length;
    btns[n].focus();activateTab(btns[n].dataset.tab);
  });
})();

// ── Deep-linking ─────────────────────────────────────────────────────────────
function writeURL(){
  try{
    const q=new URLSearchParams();
    if(S.sel)q.set("c",S.sel.slug);
    const t=currentTab();if(t&&t!=="resumen")q.set("t",t);
    history.replaceState(null,"",location.pathname+(q.toString()?"?"+q.toString():""));
  }catch(e){}
}

function applyURL(){
  const q=new URLSearchParams(location.search);
  const c=q.get("c"),t=q.get("t");
  const entry=c?S.index.find(e=>e.slug===c):null;
  const slug=entry?entry.slug:(S.index.length?S.index[0].slug:null);
  if(!slug)return;
  loadCity(slug).then(()=>{if(t&&document.getElementById("p-"+t))activateTab(t);});
}

// ── Selector de ciudad ───────────────────────────────────────────────────────
function buildSelector(){
  const sel=document.getElementById("city-sel");
  sel.innerHTML=S.index.map(c=>`<option value="${c.slug}">${c.ciudad} · EOD ${c.anio}</option>`).join("");
  sel.onchange=()=>loadCity(sel.value);
  const hs=document.getElementById("hero-stats");
  if(hs&&S.index.length){
    const tv=S.index.reduce((a,c)=>a+(c.viajes||0),0);
    const tz=S.index.reduce((a,c)=>a+(c.n_zonas||0),0);
    hs.textContent=S.index.length+" ciudades · "+fmtM(tv)+" viajes/día expandidos · "
      +tz.toLocaleString("es-CL")+" zonas georeferenciadas";
  }
  buildSidebarList();
}

function buildSidebarList(){
  const list=document.getElementById("city-list");if(!list)return;
  list.innerHTML=S.index.map(c=>{
    const meta=c.pct_publico!=null?`EOD ${c.anio} · ${fmt(c.pct_publico,1)}% púb.`:`EOD ${c.anio}`;
    return `<button class="city-item" data-slug="${c.slug}" onclick="loadCity('${c.slug}');closeSidebarMobile()">
      <span class="cn">${c.ciudad}</span>
      <span class="cm">${meta}</span>
    </button>`;
  }).join("");
}

function updateSidebarActive(slug){
  document.querySelectorAll("#city-list .city-item").forEach(b=>{
    b.classList.toggle("active",b.dataset.slug===slug);
  });
  // Scroll active item into view
  const active=document.querySelector("#city-list .city-item.active");
  if(active)active.scrollIntoView({block:"nearest",behavior:"smooth"});
}

function openSidebarMobile(){
  document.getElementById("sidebar").classList.add("open");
  document.getElementById("sidebarOverlay").classList.add("active");
  document.body.style.overflow="hidden";
}

function closeSidebarMobile(){
  document.getElementById("sidebar").classList.remove("open");
  document.getElementById("sidebarOverlay").classList.remove("active");
  document.body.style.overflow="";
}

// ── Fetch ciudad (sin cambiar ciudad activa) ─────────────────────────────────
function fetchCityData(slug){
  if(!slug)return Promise.resolve(null);
  if(S.data[slug])return Promise.resolve(S.data[slug]);
  return getJSON("data/eod/"+slug+".json").then(d=>{
    S.data[slug]=d;return d;
  }).catch(e=>{console.error("Error fetching",slug,e);return null;});
}

// ── Carga de ciudad ──────────────────────────────────────────────────────────
function loadCity(slug){
  if(!slug)return Promise.resolve();
  if(S.data[slug]){
    S.sel=S.data[slug];
    document.getElementById("city-sel").value=slug;
    updateSidebarActive(slug);
    render();return Promise.resolve();
  }
  return getJSON("data/eod/"+slug+".json").then(d=>{
    S.data[slug]=d;S.sel=d;
    document.getElementById("city-sel").value=slug;
    updateSidebarActive(slug);
    render();
  }).catch(e=>console.error("Error cargando",slug,e));
}

// ── Render general ───────────────────────────────────────────────────────────
function render(){
  const d=S.sel;if(!d)return;
  document.getElementById("res-title").innerHTML=d.ciudad+'<span class="bar"></span>';
  document.getElementById("res-lead").innerHTML=
    'Encuesta Origen-Destino <b>'+d.anio+'</b> · '+
    d.kpis.total_viajes.toLocaleString("es-CL")+' viajes expandidos en día laboral · '+
    (d.zonas?d.zonas.length:0)+' zonas georeferenciadas.';
  const nc=document.getElementById("nav-city");
  if(nc)nc.textContent=d.ciudad;
  const nch=document.getElementById("nav-chip");
  if(nch)nch.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg> EOD '+d.anio;
  renderResumen(d);
  const t=currentTab();
  if(t==="movilidad")   renderMovilidad(d);
  else if(t==="demografia") renderDemografia(d);
  else if(t==="ingreso")    renderIngreso(d);
  else if(t==="mapas")      renderMapas(d);
  else if(t==="nacional")   renderNacional();
  else if(t==="comparador") renderComparador();
  writeURL();
}

// ── TAB 1: RESUMEN ────────────────────────────────────────────────────────────
function renderResumen(d){
  const k=d.kpis;

  const topProp=d.proposito&&d.proposito.length?[...d.proposito].sort((a,b)=>b.pct-a.pct)[0]:null;

  let html=`
    <div class="kpi" style="--kpi-c:var(--navy)"><div class="v">${fmtM(k.total_viajes)}</div><div class="l">Viajes en día laboral</div><div class="s">viajes expandidos</div></div>
    <div class="kpi" style="--kpi-c:var(--mut3)"><div class="v">${k.tiempo_medio_min!=null?fmt(k.tiempo_medio_min,0)+" min":"s/d"}</div><div class="l">Tiempo medio de viaje</div><div class="s">minutos por viaje</div></div>
    <div class="kpi" style="--kpi-c:var(--navy2)"><div class="v c-navy">${pct(k.pct_publico)}</div><div class="l">Transporte público</div><div class="s">% del total</div></div>
    <div class="kpi" style="--kpi-c:var(--red)"><div class="v red">${pct(k.pct_privado)}</div><div class="l">Transporte privado</div><div class="s">automóvil y moto</div></div>
    <div class="kpi" style="--kpi-c:var(--green)"><div class="v green">${pct(k.pct_caminata)}</div><div class="l">Caminata</div><div class="s">viajes a pie</div></div>
    <div class="kpi" style="--kpi-c:var(--green)"><div class="v lime">${pct(k.pct_bicicleta)}</div><div class="l">Bicicleta</div><div class="s">y otros ciclos</div></div>`;

  if(k.dist_mediana!=null)
    html+=`<div class="kpi" style="--kpi-c:var(--or)"><div class="v or">${fmt(k.dist_mediana,1)} km</div><div class="l">Distancia mediana</div><div class="s">centroide a centroide</div></div>`;
  if(k.viajes_persona!=null)
    html+=`<div class="kpi" style="--kpi-c:var(--teal)"><div class="v c-teal">${fmt(k.viajes_persona,2)}</div><div class="l">Viajes por persona</div><div class="s">viajes / habitante día laboral</div></div>`;
  if(k.viajes_hogar!=null)
    html+=`<div class="kpi" style="--kpi-c:var(--mut3)"><div class="v">${fmt(k.viajes_hogar,1)}</div><div class="l">Viajes por hogar</div><div class="s">viajes / hogar día laboral</div></div>`;
  if(k.pct_trabajo!=null)
    html+=`<div class="kpi" style="--kpi-c:var(--navy2)"><div class="v c-navy">${pct(k.pct_trabajo)}</div><div class="l">Motivo trabajo</div><div class="s">% del total de viajes</div></div>`;
  if(k.pct_estudio!=null)
    html+=`<div class="kpi" style="--kpi-c:var(--teal)"><div class="v c-teal">${pct(k.pct_estudio)}</div><div class="l">Motivo estudio</div><div class="s">% del total de viajes</div></div>`;

  document.getElementById("res-kpis").innerHTML=html;

  renderHorario(d);
  renderDistancia(d);
}

// ── Histograma horario (total / por modo / por propósito) ────────────────────
document.querySelectorAll("#hor-seg button").forEach(b=>
  b.onclick=()=>{
    horSeg=b.dataset.hseg;
    document.querySelectorAll("#hor-seg button").forEach(x=>x.classList.toggle("on",x===b));
    if(S.sel)renderHorario(S.sel);
  });

// Ticks de hora: mostrar solo horas pares para no saturar el eje
function hourTicks(){
  return {
    font:{size:10},autoSkip:false,maxRotation:0,
    callback:function(v,i){return i%2===0?this.getLabelForValue(v):"";}
  };
}
// Título de tooltip con rango horario real
function hourTooltipTitle(items){
  const h=parseInt(items[0].label);
  if(isNaN(h))return items[0].label;
  const p=String(h).padStart(2,"0");
  return p+":00 – "+p+":59";
}

function renderHorario(d){
  const ctx=document.getElementById("c-horario");if(!ctx)return;
  if(CH.horario){CH.horario.destroy();CH.horario=null;}
  const sep=isDark()?"#161b22":"#ffffff";
  const segData=horSeg==="modo"?d.horario_modal:
                horSeg==="proposito"?d.horario_proposito:null;
  const showTotal=horSeg==="total"||!segData;
  const leg=document.getElementById("hor-leyenda");
  if(leg)leg.style.display=showTotal?"":"none";

  if(!showTotal){
    CH.horario=new Chart(ctx,{
      type:"bar",
      data:{
        labels:segData.labels,
        datasets:segData.datasets.map(ds=>({
          label:ds.label,data:ds.data,backgroundColor:ds.color,
          borderColor:sep,borderWidth:1,borderSkipped:false,
          barPercentage:1,categoryPercentage:1
        }))
      },
      options:{
        maintainAspectRatio:false,
        plugins:{
          legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:8,padding:10,font:{size:11}}},
          datalabels:{display:false},
          tooltip:{callbacks:{
            title:hourTooltipTitle,
            label:c=>c.dataset.label+": "+c.parsed.y.toFixed(2)+"% del día"
          }}
        },
        scales:{
          x:{stacked:true,ticks:hourTicks(),grid:{display:false}},
          y:{stacked:true,ticks:{callback:v=>v+"%",font:{size:10}},grid:{color:"rgba(20,40,70,.05)"}}
        }
      }
    });
    return;
  }

  if(!d.horario||!d.horario.length)return;
  CH.horario=new Chart(ctx,{
    type:"bar",
    data:{
      labels:d.horario.map(h=>h.h+"h"),
      datasets:[{
        data:d.horario.map(h=>h.pct),
        backgroundColor:d.horario.map(h=>horaColor(h.h)),
        borderColor:sep,borderWidth:1,borderSkipped:false,
        barPercentage:1,categoryPercentage:1
      }]
    },
    options:{
      maintainAspectRatio:false,
      plugins:{
        legend:{display:false},
        datalabels:{display:false},
        tooltip:{callbacks:{
          title:hourTooltipTitle,
          label:c=>c.parsed.y.toFixed(2)+"% de los viajes"
        }}
      },
      scales:{
        x:{ticks:hourTicks(),grid:{display:false}},
        y:{ticks:{callback:v=>v+"%"},grid:{color:"rgba(20,40,70,.05)"}}
      }
    }
  });
}

// ── Barras horizontales simples (hBarChart) ──────────────────────────────────
function hBarChart(id,labels,data,colors,unit){
  const ctx=document.getElementById(id);if(!ctx)return;
  if(CH[id])CH[id].destroy();
  if(!labels||!labels.length)return;
  const maxVal=Math.max(...data.filter(v=>v!=null));
  CH[id]=new Chart(ctx,{
    type:"bar",
    data:{labels,datasets:[{data,backgroundColor:colors,borderWidth:0,borderRadius:4}]},
    options:{
      indexAxis:"y",maintainAspectRatio:false,
      layout:{padding:{right:46}},
      plugins:{
        legend:{display:false},
        datalabels:{
          display:true,anchor:"end",align:"end",clamp:true,
          color:isDark()?"#8b949e":"#64748b",
          font:{size:10,weight:"700"},
          formatter:v=>v!=null?fmt(v,1)+unit:""
        },
        tooltip:{callbacks:{label:c=>fmt(c.parsed.x,1)+unit}}
      },
      scales:{
        x:{display:false,max:maxVal*1.22},
        y:{ticks:{font:{size:12}},grid:{display:false}}
      }
    }
  });
}

// ── Barras apiladas horizontales (cross-tabs) ────────────────────────────────
function stackedBar(id,chartData){
  if(!chartData)return;
  const ctx=document.getElementById(id);if(!ctx)return;
  if(CH[id])CH[id].destroy();
  const{labels,datasets}=chartData;
  if(!labels||!datasets||!labels.length)return;
  CH[id]=new Chart(ctx,{
    type:"bar",
    data:{
      labels,
      datasets:datasets.map(ds=>({
        label:ds.label,
        data:ds.data,
        backgroundColor:ds.color||GREY,
        borderWidth:0,
      }))
    },
    options:{
      indexAxis:"y",maintainAspectRatio:false,
      plugins:{
        legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:8,padding:10,font:{size:11}}},
        datalabels:{
          display:ctx=>{const v=ctx.dataset.data[ctx.dataIndex];return v!=null&&v>=8;},
          anchor:"center",align:"center",
          color:"#fff",
          font:{size:10,weight:"700"},
          formatter:v=>v!=null&&v>=8?Math.round(v)+"%":""
        },
        tooltip:{callbacks:{label:c=>c.dataset.label+": "+fmt(c.parsed.x,1)+"%"}}
      },
      scales:{
        x:{stacked:true,display:false,max:100},
        y:{stacked:true,ticks:{font:{size:11}},grid:{display:false}}
      }
    }
  });
}

// ── Distribución por distancia (total / desglose modal) ──────────────────────
document.querySelectorAll("#dist-seg button").forEach(b=>
  b.onclick=()=>{
    distSeg=b.dataset.dseg;
    document.querySelectorAll("#dist-seg button").forEach(x=>x.classList.toggle("on",x===b));
    if(S.sel)renderDistancia(S.sel);
  });

function renderDistancia(d){
  const ctx=document.getElementById("c-distancia");if(!ctx)return;
  if(CH["c-distancia"]){CH["c-distancia"].destroy();CH["c-distancia"]=null;}
  const sep=isDark()?"#161b22":"#ffffff";
  const lblColor=isDark()?"#8b949e":"#64748b";

  if(distSeg==="modo"&&d.dist_modal){
    const dm=d.dist_modal;
    const totals=dm.labels.map((_,i)=>dm.datasets.reduce((a,ds)=>a+(ds.data[i]||0),0));
    const maxT=Math.max(...totals);
    CH["c-distancia"]=new Chart(ctx,{
      type:"bar",
      data:{
        labels:dm.labels.map(t=>t+" km"),
        datasets:dm.datasets.map(ds=>({
          label:ds.label,data:ds.data,backgroundColor:ds.color,
          borderColor:sep,borderWidth:1,borderSkipped:false,
          barPercentage:1,categoryPercentage:1
        }))
      },
      options:{
        maintainAspectRatio:false,
        plugins:{
          legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:8,padding:10,font:{size:11}}},
          datalabels:{
            display:c=>c.datasetIndex===c.chart.data.datasets.length-1,
            anchor:"end",align:"end",clamp:true,
            color:lblColor,font:{size:10,weight:"700"},
            formatter:(v,c)=>{
              const t=c.chart.data.datasets.reduce((a,ds)=>a+(ds.data[c.dataIndex]||0),0);
              return t>0.5?fmt(t,1)+"%":"";
            }
          },
          tooltip:{callbacks:{
            label:c=>{
              const t=c.chart.data.datasets.reduce((a,ds)=>a+(ds.data[c.dataIndex]||0),0);
              const share=t>0?c.parsed.y/t*100:0;
              return c.dataset.label+": "+fmt(c.parsed.y,1)+"% del total · "+fmt(share,0)+"% del tramo";
            }
          }}
        },
        scales:{
          x:{stacked:true,ticks:{font:{size:11}},grid:{display:false}},
          y:{stacked:true,display:false,max:maxT*1.3}
        }
      }
    });
    return;
  }

  if(!d.distancia||!d.distancia.length)return;
  const maxV=Math.max(...d.distancia.map(t=>t.pct||0));
  // % acumulado: qué proporción de los viajes recorre hasta ese tramo
  let acc=0;
  const cum=d.distancia.map(t=>{acc+=t.pct||0;return Math.round(acc*10)/10;});
  const lineColor=isDark()?"#79c0ff":NAVY2;
  CH["c-distancia"]=new Chart(ctx,{
    type:"bar",
    data:{
      labels:d.distancia.map(t=>t.tramo+" km"),
      datasets:[
        {
          data:d.distancia.map(t=>t.pct),
          backgroundColor:d.distancia.map(t=>TRAMO_PAL[t.tramo]||"#41ab5d"),
          borderColor:sep,borderWidth:1,borderSkipped:false,
          barPercentage:1,categoryPercentage:1,order:2,
          datalabels:{
            display:true,anchor:"end",align:"end",clamp:true,
            color:lblColor,font:{size:10,weight:"700"},
            formatter:v=>v>0.5?fmt(v,1)+"%":""
          }
        },
        {
          type:"line",label:"% acumulado",data:cum,
          borderColor:lineColor,borderWidth:2,borderDash:[5,4],
          pointRadius:3,pointBackgroundColor:lineColor,
          tension:0.35,yAxisID:"y1",order:1,
          datalabels:{display:false}
        }
      ]
    },
    options:{
      maintainAspectRatio:false,
      plugins:{
        legend:{
          display:true,position:"bottom",
          labels:{usePointStyle:true,boxWidth:8,padding:8,font:{size:11},
            filter:item=>item.text==="% acumulado"}
        },
        tooltip:{callbacks:{
          label:c=>c.dataset.label==="% acumulado"
            ?"Acumulado: "+fmt(c.parsed.y,1)+"% de los viajes hasta este tramo"
            :fmt(c.parsed.y,1)+"% de los viajes"
        }}
      },
      scales:{
        x:{ticks:{font:{size:11}},grid:{display:false}},
        y:{display:false,max:maxV*1.3},
        y1:{display:false,min:0,max:108}
      }
    }
  });
}

// ── TAB 2: MODOS ─────────────────────────────────────────────────────────────
function renderMovilidad(d){
  renderModal(d);renderProp(d);renderEtario(d);renderQuintil(d);
  renderHorarioModal(d);renderPropModo(d);
}

function renderModal(d){
  if(!d.modal||!d.modal.length)return;
  hBarChart("c-modal",d.modal.map(m=>m.modo),d.modal.map(m=>m.pct),
    d.modal.map(m=>MODO_COL[m.modo]||GREY),"%");
}
function renderProp(d){
  if(!d.proposito||!d.proposito.length)return;
  hBarChart("c-prop",d.proposito.map(p=>p.prop),d.proposito.map(p=>p.pct),
    d.proposito.map(p=>PROP_COL[p.prop]||GREY),"%");
}
function renderEtario(d){
  if(!d.etario||!d.etario.length)return;
  hBarChart("c-etario",d.etario.map(e=>e.grupo),d.etario.map(e=>e.pct),
    d.etario.map((_,i)=>ETARIO_PAL[i]||NAVY),"%");
}
function renderQuintil(d){
  if(!d.quintil||!d.quintil.length)return;
  hBarChart("c-quintil",
    d.quintil.map(q=>"Q"+q.q+" · "+(["Bajo","Medio-bajo","Medio","Medio-alto","Alto"][q.q-1]||"")),
    d.quintil.map(q=>q.pct),QUINTIL_COL,"%");
}

function renderHorarioModal(d){
  if(!d.horario_modal)return;
  if(CH["c-horario-modal"])CH["c-horario-modal"].destroy();
  const ctx=document.getElementById("c-horario-modal");if(!ctx)return;
  const{labels,datasets}=d.horario_modal;
  // Composición modal: normalizar cada hora a 100% (la magnitud horaria ya
  // está en el histograma del Resumen; aquí interesa el mix de modos)
  const totals=labels.map((_,i)=>datasets.reduce((a,ds)=>a+(ds.data[i]||0),0));
  const norm=datasets.map(ds=>({
    label:ds.label,color:ds.color,
    data:ds.data.map((v,i)=>totals[i]>0.05?Math.round((v||0)/totals[i]*1000)/10:null)
  }));
  const sep=isDark()?"#161b22":"#ffffff";
  CH["c-horario-modal"]=new Chart(ctx,{
    type:"bar",
    data:{
      labels,
      datasets:norm.map(ds=>({
        label:ds.label,data:ds.data,backgroundColor:ds.color,
        borderColor:sep,borderWidth:1,borderSkipped:false,
        barPercentage:1,categoryPercentage:1
      }))
    },
    options:{
      maintainAspectRatio:false,
      plugins:{
        legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:8,padding:12,font:{size:11}}},
        datalabels:{display:false},
        tooltip:{callbacks:{
          title:hourTooltipTitle,
          label:c=>c.dataset.label+": "+fmt(c.parsed.y,1)+"% de los viajes de esa hora"
        }}
      },
      scales:{
        x:{stacked:true,ticks:hourTicks(),grid:{display:false}},
        y:{stacked:true,min:0,max:100,ticks:{callback:v=>v+"%",font:{size:10},stepSize:25},grid:{color:"rgba(20,40,70,.05)"}}
      }
    }
  });
}

function renderPropModo(d){
  if(!d.prop_modo)return;
  stackedBar("c-prop-modo",d.prop_modo);
}

// ── TAB 3: DEMOGRAFÍA ────────────────────────────────────────────────────────
function renderDemografia(d){
  if(d.tipo_usuario&&d.tipo_usuario.length){
    hBarChart("c-tipo-usuario",
      d.tipo_usuario.map(u=>u.tipo),
      d.tipo_usuario.map(u=>u.pct),
      USUARIO_PAL.slice(0,d.tipo_usuario.length),"%");
  }
  stackedBar("c-modal-etario",d.modal_etario);
  stackedBar("c-modal-usuario",d.modal_usuario);
  stackedBar("c-prop-etario",d.prop_etario);
}

// ── TAB 4: INGRESO ───────────────────────────────────────────────────────────
function renderIngreso(d){
  stackedBar("c-modal-quintil",d.modal_quintil);
  stackedBar("c-dist-quintil",d.dist_quintil);
  stackedBar("c-dist-modo",d.dist_modo);
}

// ── TAB 5: MAPAS OD ──────────────────────────────────────────────────────────
const MAP_DESC={
  gen:"Viajes <b>generados</b> por zona (salidas desde el origen). Mapa coroplético: a mayor intensidad de naranjo, más viajes.",
  atr:"Viajes <b>atraídos</b> por zona (llegadas al destino). Mapa coroplético: a mayor intensidad de azul, más viajes.",
  od :"Cada arco une dos zonas: el <b>grosor</b> indica cuántos viajes se realizan entre ellas y la <b>flecha</b> marca el <b>sentido dominante</b>. Haz clic en un arco para el detalle por sentido."
};
const MAP_NOTE={
  gen:"Fuente: EOD procesada. Color de cada zona proporcional al volumen de viajes generado (factor de expansión).",
  atr:"Fuente: EOD procesada. Color de cada zona proporcional al volumen de viajes atraído (factor de expansión).",
  od :"Pares OD por volumen de viajes expandidos. Las líneas son de deseo — no representan rutas reales."
};

document.querySelectorAll(".ctrl button[data-view]").forEach(b=>
  b.onclick=()=>setMapView(b.dataset.view));

document.querySelectorAll("#per-ctrl button").forEach(b=>
  b.onclick=()=>{
    odPer=b.dataset.per;
    document.querySelectorAll("#per-ctrl button").forEach(x=>x.classList.toggle("on",x===b));
    updateMapNote();
    if(S.sel)drawMapView(S.sel);
  });

(function(){
  const r=document.getElementById("od-n");if(!r)return;
  r.addEventListener("input",()=>{
    odTopN=+r.value;
    const v=document.getElementById("od-n-val");if(v)v.textContent=odTopN;
    updateMapNote();
    if(S.sel&&mapView==="od")drawMapView(S.sel);
  });
})();

document.querySelectorAll("#esc-ctrl button").forEach(b=>
  b.onclick=()=>{
    odEsc=b.dataset.esc;
    document.querySelectorAll("#esc-ctrl button").forEach(x=>x.classList.toggle("on",x===b));
    if(S.sel&&mapView==="od")drawMapView(S.sel);
  });

function updateMapNote(){
  const note=document.getElementById("map-note");if(!note)return;
  const per=odPer==="all"?"":" · "+PER_LBL[odPer];
  note.textContent=mapView==="od"
    ?`Top ${odTopN} pares OD por volumen de viajes expandidos${per}. Grosor proporcional al flujo — las líneas son de deseo, no rutas reales.`
    :MAP_NOTE[mapView]+(per?" Período:"+per.slice(2)+".":"");
}

function setMapView(v){
  mapView=v;
  document.querySelectorAll(".ctrl button[data-view]").forEach(b=>b.classList.toggle("on",b.dataset.view===v));
  document.getElementById("map-desc").innerHTML=MAP_DESC[v];
  const nw=document.getElementById("odn-wrap");
  if(nw)nw.style.display=v==="od"?"":"none";
  const ew=document.getElementById("esc-wrap");
  if(ew)ew.style.display=v==="od"?"":"none";
  updateMapNote();
  if(S.sel)drawMapView(S.sel);
}

function ensureOdMap(){
  if(odMap)return;
  odMap=L.map("od-map",{preferCanvas:true}).setView([-33.5,-70.7],11);
  mapChrome(odMap);
  odInfo=L.control({position:"topright"});
  odInfo.onAdd=function(){this._d=L.DomUtil.create("div","info");this._d.innerHTML="<b>Pasa el cursor</b><br>sobre una zona";return this._d;};
  odInfo.update=function(html){this._d.innerHTML=html||"<b>Pasa el cursor</b><br>sobre una zona";};
  odInfo.addTo(odMap);
  odLegend=L.control({position:"bottomright"});
  odLegend.onAdd=function(){this._d=L.DomUtil.create("div","legend");return this._d;};
  odLegend.addTo(odMap);
}

function drawMapView(d){
  ensureOdMap();
  if(odLyr){odMap.removeLayer(odLyr);odLyr=null;}
  odInfo.update(null);
  if(mapView==="gen"||mapView==="atr")drawChoropleth(d,mapView);
  else drawODLines(d);
}

function drawCircles(d,view){
  const zones=d.zonas;
  if(!zones||!zones.length){odInfo.update("Sin datos de zonas.");return;}
  const getV=z=>{
    if(odPer==="all")return view==="gen"?z.gen:z.atr;
    const p=z.per&&z.per[odPer];
    return p?(view==="gen"?p[0]:p[1]):0;
  };
  const maxVal=Math.max(...zones.map(getV));
  const color=view==="gen"?OR:NAVY;
  const lbl=view==="gen"?"Generación":"Atracción";
  const perTxt=odPer==="all"?"":"<br><small>"+PER_LBL[odPer]+"</small>";
  if(!maxVal){odInfo.update("Sin datos para este período.");odLegend._d.innerHTML="";return;}
  const lyr=L.layerGroup();
  zones.forEach(z=>{
    const val=getV(z);if(!val)return;
    const r=4+Math.sqrt(val/maxVal)*22;
    const m=L.circleMarker([z.lat,z.lng],{
      radius:r,color:"rgba(255,255,255,.55)",weight:1,
      fillColor:color,fillOpacity:0.72
    });
    m.on("mouseover",()=>{
      m.setStyle({fillOpacity:.92,weight:2});
      odInfo.update(`<b>Zona ${z.zona}</b>${perTxt}<br>${lbl}:<br><b>${val.toLocaleString("es-CL")} viajes</b>`);
    });
    m.on("mouseout",()=>{m.setStyle({fillOpacity:.72,weight:1});odInfo.update(null);});
    m.bindPopup(`<b>Zona ${z.zona}</b>${perTxt}<br>${lbl}: <b>${val.toLocaleString("es-CL")} viajes</b>`);
    lyr.addLayer(m);
  });
  lyr.addTo(odMap);odLyr=lyr;
  odLegend._d.innerHTML='<b>'+lbl+'</b>'+
    [["8","Bajo","0.4"],["14","Medio","0.65"],["20","Alto","0.85"]].map(([sz,lab,op])=>
      `<div style="display:flex;align-items:center;gap:7px;margin:3px 0">
        <span style="display:inline-block;width:${sz}px;height:${sz}px;border-radius:50%;background:${color};opacity:${op}"></span>${lab}
      </div>`).join("");
  const pts=zones.filter(z=>getV(z)>0).map(z=>[z.lat,z.lng]);
  if(pts.length)odMap.fitBounds(L.latLngBounds(pts).pad(0.1));
}

// ── Mapa COROPLÉTICO de generación / atracción (polígonos de zona coloreados) ──
const GEOCACHE={};
const nz=z=>String(z).replace(/\.0$/,"").trim();
function hexMix(a,b,t){
  const pa=[1,3,5].map(i=>parseInt(a.slice(i,i+2),16)), pb=[1,3,5].map(i=>parseInt(b.slice(i,i+2),16));
  return "#"+pa.map((v,i)=>Math.round(v+(pb[i]-v)*t).toString(16).padStart(2,"0")).join("");
}
function drawChoropleth(d,view){
  const zones=d.zonas;
  if(!zones||!zones.length){odInfo.update("Sin datos de zonas.");return;}
  const getV=z=>{
    if(odPer==="all")return view==="gen"?z.gen:z.atr;
    const p=z.per&&z.per[odPer];
    return p?(view==="gen"?p[0]:p[1]):0;
  };
  const base=view==="gen"?OR:NAVY;
  const light=view==="gen"?"#fbe8cf":"#dbe7f5";
  const lbl=view==="gen"?"Generación":"Atracción";
  const perTxt=odPer==="all"?"":"<br><small>"+PER_LBL[odPer]+"</small>";
  const valBy={}; zones.forEach(z=>{valBy[nz(z.zona)]=getV(z);});
  const pos=zones.map(getV).filter(v=>v>0).sort((a,b)=>a-b);
  if(!pos.length){odInfo.update("Sin datos para este período.");odLegend._d.innerHTML="";return;}
  const q=p=>pos[Math.min(pos.length-1,Math.floor(p*pos.length))];
  const brks=[q(.2),q(.4),q(.6),q(.8)];
  const ramp=[0,1,2,3,4].map(i=>hexMix(light,base,0.18+0.82*i/4));
  const binOf=v=>{let b=0;for(const t of brks)if(v>t)b++;return b;};
  const render=geo=>{
    if(odLyr){odMap.removeLayer(odLyr);odLyr=null;}
    let matched=0;
    const lyr=L.geoJSON(geo,{
      style:f=>{
        const v=valBy[nz(f.properties.zona)]||0; if(v>0)matched++;
        return {fillColor:v>0?ramp[binOf(v)]:(isDark()?"#1a2230":"#e8eaee"),
          fillOpacity:v>0?0.82:0.18, color:isDark()?"#0b1220":"#ffffff", weight:0.5};
      },
      onEachFeature:(f,layer)=>{
        const z=nz(f.properties.zona),v=valBy[z]||0;
        layer.on("mouseover",()=>{layer.setStyle({weight:2.2,color:base,fillOpacity:.95});layer.bringToFront();
          odInfo.update(`<b>Zona ${z}</b>${perTxt}<br>${lbl}:<br><b>${v.toLocaleString("es-CL")} viajes</b>`);});
        layer.on("mouseout",()=>{lyr.resetStyle(layer);odInfo.update(null);});
        layer.bindPopup(`<b>Zona ${z}</b>${perTxt}<br>${lbl}: <b>${v.toLocaleString("es-CL")} viajes</b>`);
      }
    });
    if(!matched){drawCircles(d,view);return;}   // sin coincidencias -> respaldo a círculos
    lyr.addTo(odMap);odLyr=lyr;
    const fmt=n=>Math.round(n).toLocaleString("es-CL");
    const rows=[[0,"< "+fmt(brks[0])],[1,fmt(brks[0])+"–"+fmt(brks[1])],[2,fmt(brks[1])+"–"+fmt(brks[2])],
                [3,fmt(brks[2])+"–"+fmt(brks[3])],[4,"> "+fmt(brks[3])]];
    odLegend._d.innerHTML='<b>'+lbl+'</b><br><small>viajes por zona</small>'+rows.map(([i,lab])=>
      `<div style="display:flex;align-items:center;gap:7px;margin:3px 0">
        <span style="display:inline-block;width:16px;height:12px;background:${ramp[i]};border:1px solid rgba(0,0,0,.18)"></span>${lab}</div>`).join("");
    try{odMap.fitBounds(lyr.getBounds().pad(0.05));}catch(e){}
  };
  if(GEOCACHE[d.ciudad]){render(GEOCACHE[d.ciudad]);return;}
  odInfo.update("Cargando zonas…");
  getJSON("data/geojson/"+encodeURIComponent(d.ciudad)+".geojson").then(geo=>{
    GEOCACHE[d.ciudad]=geo;
    if(S.sel&&S.sel.ciudad===d.ciudad&&(mapView==="gen"||mapView==="atr"))render(geo);
  }).catch(e=>{console.warn("geojson no disponible para",d.ciudad,"- respaldo a círculos",e);drawCircles(d,view);});
}

// Arco cuadrático de Bézier entre dos puntos lat/lng (curvatura perpendicular)
function odCurve(a,b,curv){
  const mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2;
  const dx=b[0]-a[0],dy=b[1]-a[1];
  const cx=mx-dy*curv,cy=my+dx*curv;
  const pts=[];
  for(let i=0;i<=24;i++){
    const t=i/24,u=1-t;
    pts.push([u*u*a[0]+2*u*t*cx+t*t*b[0],u*u*a[1]+2*u*t*cy+t*t*b[1]]);
  }
  return pts;
}

function drawODLines(d){
  // Escala efectiva: comunas en áreas metropolitanas, sectores con
  // zonificación fina, zonas en el resto
  const tieneCom=!!(d.od_comuna&&d.od_comuna.all&&d.od_comuna.all.length);
  const cb=document.querySelector('#esc-ctrl button[data-esc="comunas"]');
  if(cb)cb.style.display=tieneCom?"":"none";
  let escEff=odEsc;
  if(odEsc==="auto"){
    escEff=(tieneCom&&d.od_comuna.ncom>=4)?"comunas"
      :((d.od_macro&&d.zonas&&d.zonas.length>120)?"sectores":"zonas");
  }else if(odEsc==="comunas"&&!tieneCom){
    escEff=d.od_macro?"sectores":"zonas";
  }else if(odEsc==="sectores"&&!d.od_macro){
    escEff="zonas";
  }
  const usaAgg=escEff!=="zonas";
  const flows=escEff==="comunas"?(d.od_comuna[odPer]||[])
    :escEff==="sectores"?(d.od_macro&&d.od_macro[odPer])||[]
    :(odPer==="all"?d.od_top:(d.od_per&&d.od_per[odPer])||[]);
  if(!flows||!flows.length){
    odInfo.update(odPer==="all"?"Sin datos de flujos OD.":"Sin flujos para este período.");
    odLegend._d.innerHTML="";return;
  }
  const uni=escEff==="zonas"?"Zona ":"";
  const perTxt=odPer==="all"?"":"<br><small>"+PER_LBL[odPer]+"</small>";
  // Agregar pares bidireccionales: A⇄B con flujo por sentido
  const agg={};
  flows.forEach(f=>{
    const k=f.o<f.d?f.o+"|"+f.d:f.d+"|"+f.o;
    if(!agg[k])agg[k]={o:f.o,d:f.d,no:f.no,nd:f.nd,olat:f.olat,olng:f.olng,dlat:f.dlat,dlng:f.dlng,ab:0,ba:0};
    const e=agg[k];
    if(f.o===e.o)e.ab+=f.n;else e.ba+=f.n;
  });
  let pairs=Object.values(agg);
  pairs.forEach(p=>p.total=p.ab+p.ba);
  pairs.sort((x,y)=>y.total-x.total);
  const totalPairs=pairs.length;
  pairs=pairs.slice(0,odTopN);
  const maxT=pairs[0].total||1;
  const lineCol=isDark()?"#e3b341":OR;
  const arrowCol=isDark()?"#79c0ff":NAVY;
  const lyr=L.layerGroup();
  const nodes=new Map();
  pairs.forEach(p=>{
    const fwd=p.ab>=p.ba;                       // sentido dominante
    const A=fwd?[p.olat,p.olng]:[p.dlat,p.dlng];
    const B=fwd?[p.dlat,p.dlng]:[p.olat,p.olng];
    const pts=odCurve(A,B,0.18);
    const w=1.4+(p.total/maxT)*8;
    const op=0.5+(p.total/maxT)*0.35;
    const line=L.polyline(pts,{color:lineCol,weight:w,opacity:op,lineCap:"round"});
    const tip=`<b>${uni}${p.o} ⇄ ${uni}${p.d}</b>${perTxt}`+
      (usaAgg?`<br><small>${p.no||"?"} y ${p.nd||"?"} zonas agrupadas</small>`:"")+
      `<br>${p.o} → ${p.d}: <b>${p.ab.toLocaleString("es-CL")}</b>`+
      `<br>${p.d} → ${p.o}: <b>${p.ba.toLocaleString("es-CL")}</b>`+
      `<br>Total: <b>${p.total.toLocaleString("es-CL")} viajes</b>`;
    line.on("mouseover",()=>{line.setStyle({weight:w+2,opacity:1});odInfo.update(tip);});
    line.on("mouseout",()=>{line.setStyle({weight:w,opacity:op});odInfo.update(null);});
    line.bindPopup(tip);
    lyr.addLayer(line);
    // Flecha del sentido dominante a ~55% del arco, rotada según tangente
    const i1=Math.max(1,Math.floor(pts.length*0.55));
    const p0=pts[i1-1],p1=pts[i1];
    const mid=[(p0[0]+p1[0])/2,(p0[1]+p1[1])/2];
    const sx=(p1[1]-p0[1])*Math.cos(mid[0]*Math.PI/180),sy=-(p1[0]-p0[0]);
    const deg=Math.round(Math.atan2(sy,sx)*180/Math.PI);
    const aw=Math.round(Math.max(11,Math.min(20,7+w*1.4)));
    lyr.addLayer(L.marker(mid,{interactive:false,icon:L.divIcon({
      className:"od-arrow",iconSize:[aw,aw],iconAnchor:[aw/2,aw/2],
      html:`<svg viewBox="0 0 10 10" width="${aw}" height="${aw}" style="transform:rotate(${deg}deg);display:block"><path d="M0 1.2 L10 5 L0 8.8 L2.6 5 Z" fill="${arrowCol}"/></svg>`
    })}));
    nodes.set(p.o,[p.olat,p.olng]);
    nodes.set(p.d,[p.dlat,p.dlng]);
  });
  // Nodos en los centroides (centro urbano poblacional)
  nodes.forEach((c,z)=>{
    lyr.addLayer(L.circleMarker(c,{radius:usaAgg?5:3.5,color:"#fff",weight:1.5,fillColor:arrowCol,fillOpacity:1})
      .bindTooltip(uni+z));
  });
  lyr.addTo(odMap);odLyr=lyr;
  odLegend._d.innerHTML='<b>Flujos OD</b>'+
    [["2","Bajo",".5"],["5","Medio",".7"],["8","Alto",".9"]].map(([h,lab,op])=>
      `<div style="display:flex;align-items:center;gap:7px;margin:3px 0">
        <span style="display:inline-block;width:26px;height:${h}px;background:${lineCol};opacity:${op};border-radius:2px"></span>${lab}
      </div>`).join("")+
    `<div style="display:flex;align-items:center;gap:7px;margin:3px 0">
      <svg viewBox="0 0 10 10" width="12" height="12"><path d="M0 1.2 L10 5 L0 8.8 L2.6 5 Z" fill="${arrowCol}"/></svg>sentido dominante
    </div>`;
  const note=document.getElementById("map-note");
  if(note)note.textContent="Mostrando "+pairs.length+" de "+totalPairs+" pares entre "
    +(escEff==="comunas"?"comunas (nodos en el centro urbano poblacional)"
      :escEff==="sectores"?"sectores (zonas agrupadas espacialmente)":"zonas")
    +" · grosor proporcional al flujo total, flecha = sentido dominante"
    +(odPer==="all"?"":" · "+PER_LBL[odPer])+". Líneas de deseo — no representan rutas reales.";
  const pts=pairs.flatMap(p=>[[p.olat,p.olng],[p.dlat,p.dlng]]);
  if(pts.length)odMap.fitBounds(L.latLngBounds(pts).pad(0.08));
}

function renderMapas(d){
  ensureOdMap();
  setTimeout(()=>{odMap.invalidateSize();drawMapView(d);},80);
}

// ── TAB 6: NACIONAL ──────────────────────────────────────────────────────────
function renderNacional(){
  if(!renderNacional._wired){
    renderNacional._wired=true;
    document.querySelectorAll("#nac-subtabs button").forEach(b=>{
      b.onclick=()=>{
        document.querySelectorAll("#nac-subtabs button").forEach(x=>x.classList.toggle("on",x===b));
        document.querySelectorAll("#p-nacional .sub-panel").forEach(p=>p.classList.toggle("on",p.id==="sp-"+b.dataset.sub));
        if(b.dataset.sub==="panorama")renderPanorama();
        if(b.dataset.sub==="ranking") renderRanking();
      };
    });
  }
  renderPanorama();
}

function renderPanorama(){
  if(!S.index.length)return;
  // KPIs
  const avg=f=>{const l=S.index.filter(c=>c[f]!=null);return l.length?l.reduce((a,c)=>a+c[f],0)/l.length:null;};
  const totalV=S.index.reduce((a,c)=>a+(c.viajes||0),0);
  const avgPub=avg("pct_publico"),avgDm=avg("dist_mediana");
  const nacKpis=document.getElementById("nac-kpis");
  if(nacKpis)nacKpis.innerHTML=`
    <div class="kpi" style="--kpi-c:var(--navy)"><div class="v">${S.index.length}</div><div class="l">Ciudades cubiertas</div><div class="s">EOD homologadas</div></div>
    <div class="kpi" style="--kpi-c:var(--teal)"><div class="v c-teal">${fmtM(totalV)}</div><div class="l">Viajes expandidos</div><div class="s">suma 18 ciudades día laboral</div></div>
    <div class="kpi" style="--kpi-c:var(--navy2)"><div class="v c-navy">${avgPub!=null?fmt(avgPub,1)+"%":"s/d"}</div><div class="l">% Público promedio</div><div class="s">promedio simple entre ciudades</div></div>
    <div class="kpi" style="--kpi-c:var(--or)"><div class="v or">${avgDm!=null?fmt(avgDm,1)+" km":"s/d"}</div><div class="l">Dist. mediana promedio</div><div class="s">centroide a centroide</div></div>`;
  // Map + donut (delayed so container is laid out)
  setTimeout(()=>{renderNacMap();renderNacModal();},120);
  // Table
  const nacTable=document.getElementById("nac-table");
  if(!nacTable)return;
  const rows=S.index.map(c=>{
    const sel=S.sel&&S.sel.slug===c.slug;
    return `<tr class="${sel?"nac-sel":""}" onclick="loadCity('${c.slug}');activateTab('resumen')" title="${c.ciudad}">
      <td>${c.ciudad}</td>
      <td class="num">${c.anio}</td>
      <td class="num">${fmtM(c.viajes)}</td>
      <td class="num pub-col">${c.pct_publico!=null?fmt(c.pct_publico,1)+"%":"—"}</td>
      <td class="num">${c.pct_privado!=null?fmt(c.pct_privado,1)+"%":"—"}</td>
      <td class="num">${c.pct_no_motorizado!=null?fmt(c.pct_no_motorizado,1)+"%":"—"}</td>
      <td class="num">${c.dist_mediana!=null?fmt(c.dist_mediana,1)+" km":"—"}</td>
      <td class="num">${c.viajes_persona!=null?fmt(c.viajes_persona,2):"—"}</td>
    </tr>`;
  }).join("");
  nacTable.innerHTML=`<table class="nac-tbl">
    <thead><tr>
      <th>Ciudad</th><th class="num">Año</th><th class="num">Viajes/día</th>
      <th class="num pub-col">% Público</th><th class="num">% Privado</th>
      <th class="num">% No motor.</th><th class="num">Dist. mediana</th><th class="num">V/pers.</th>
    </tr></thead><tbody>${rows}</tbody>
  </table>`;
}

function pctToColor(pct){
  if(pct==null)return GREY;
  if(pct<20)return RED;
  if(pct<30)return OR;
  if(pct<40)return TEAL;
  return NAVY;
}

function renderNacMap(){
  if(!S.index.length)return;
  const el=document.getElementById("nac-map");
  if(!el||el.offsetParent===null)return;
  if(!nacMap){
    nacMap=L.map("nac-map",{preferCanvas:true,zoomControl:true}).setView([-37,-71.5],5);
    const tile=L.tileLayer(isDark()?CARTO_DARK:CARTO_LIGHT,
      {attribution:'&copy; OpenStreetMap &copy; CARTO',maxZoom:19});
    tile.addTo(nacMap);MAPS.push({map:nacMap,carto:tile});authorWM(nacMap);
  }
  if(nacMapLyr){nacMap.removeLayer(nacMapLyr);nacMapLyr=null;}
  const maxV=Math.max(...S.index.map(c=>c.viajes||0))||1;
  const lyr=L.layerGroup();
  S.index.forEach(c=>{
    const coords=CITY_COORDS[c.slug];if(!coords)return;
    const r=7+Math.sqrt((c.viajes||0)/maxV)*26;
    const isActive=S.sel&&S.sel.slug===c.slug;
    const m=L.circleMarker(coords,{
      radius:r,color:isActive?"#fff":"rgba(255,255,255,.55)",
      weight:isActive?2.5:1.5,
      fillColor:pctToColor(c.pct_publico),
      fillOpacity:isActive?0.95:0.78
    });
    if(isActive)m.setStyle({color:OR,weight:3});
    const tip=[
      `<b>${c.ciudad}</b> · EOD ${c.anio}`,
      `${fmtM(c.viajes)} viajes/día`,
      c.pct_publico!=null?`${fmt(c.pct_publico,1)}% público`:"",
      c.viajes_persona!=null?`${fmt(c.viajes_persona,2)} v/persona`:"",
    ].filter(Boolean).join("<br>");
    m.bindTooltip(tip,{sticky:true});
    m.on("click",()=>{loadCity(c.slug);activateTab("resumen");});
    lyr.addLayer(m);
  });
  lyr.addTo(nacMap);nacMapLyr=lyr;
  setTimeout(()=>nacMap.invalidateSize(),80);
}

function renderNacModal(){
  if(!S.index.length)return;
  const ctx=document.getElementById("c-nac-modal");if(!ctx)return;
  const avg=f=>{const l=S.index.filter(c=>c[f]!=null);return l.length?l.reduce((a,c)=>a+c[f],0)/l.length:0;};
  const pub=avg("pct_publico"),priv=avg("pct_privado"),
        cam=avg("pct_caminata"),bic=avg("pct_bicicleta");
  const resto=Math.max(0,100-(pub+priv+cam+bic));
  if(CH["c-nac-modal"])CH["c-nac-modal"].destroy();
  CH["c-nac-modal"]=new Chart(ctx,{
    type:"doughnut",
    data:{
      labels:["Público","Privado","Caminata","Bicicleta","Combinado y otros"],
      datasets:[{
        data:[pub,priv,cam,bic,resto].map(v=>Math.round(v*10)/10),
        backgroundColor:[NAVY,RED,GREEN,LIME,GREY],
        borderWidth:0,hoverOffset:8
      }]
    },
    options:{
      maintainAspectRatio:false,cutout:"60%",
      plugins:{
        legend:{display:true,position:"bottom"},
        datalabels:{display:true,color:"#fff",font:{size:12,weight:"700"},
          formatter:v=>v>=5?Math.round(v)+"%":""},
        tooltip:{callbacks:{label:c=>c.label+": "+fmt(c.parsed,1)+"%"}}
      },
      __noWM:true
    }
  });
}

// ── Comparador ────────────────────────────────────────────────────────────────
function buildComparadorUI(){
  if(cmpBuilt)return;cmpBuilt=true;
  const grid=document.getElementById("cmp-city-grid");
  if(grid){
    grid.innerHTML=S.index.map((c,i)=>`
      <label class="cmp-cb${i<8?" on":""}" data-slug="${c.slug}">
        <input type="checkbox"${i<8?" checked":""}/>
        <span>${c.ciudad}</span>
      </label>`).join("");
    grid.querySelectorAll(".cmp-cb").forEach(lbl=>{
      lbl.onclick=()=>{
        const cb=lbl.querySelector("input");
        cb.checked=!cb.checked;lbl.classList.toggle("on",cb.checked);
        renderComparadorChart();
      };
    });
  }
  document.querySelectorAll("#cmp-var-ctrl button").forEach(b=>{
    b.onclick=()=>{
      document.querySelectorAll("#cmp-var-ctrl button").forEach(x=>x.classList.toggle("on",x===b));
      cmpVar=b.dataset.var;
      const ir=document.getElementById("cmp-ind-row");
      if(ir)ir.style.display=cmpVar==="indicadores"?"flex":"none";
      renderComparadorChart();
    };
  });
  const indRow=document.getElementById("cmp-ind-row");
  if(indRow)indRow.querySelectorAll("button").forEach(b=>{
    b.onclick=()=>{
      indRow.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));
      cmpIndSel=b.dataset.ind;renderComparadorChart();
    };
  });
}

function renderComparador(){buildComparadorUI();renderComparadorChart();}

async function renderComparadorChart(){
  const slugs=[...document.querySelectorAll(".cmp-cb input:checked")]
    .map(cb=>cb.closest("[data-slug]").dataset.slug);
  const wrap=document.getElementById("cmp-chart-wrap");if(!wrap)return;
  if(slugs.length<2){
    if(CH["c-comparador"]){CH["c-comparador"].destroy();CH["c-comparador"]=null;}
    wrap.innerHTML='<div class="empty" style="margin:0;height:100%;display:flex;align-items:center;justify-content:center">Selecciona al menos 2 ciudades para comparar.</div>';
    return;
  }
  if(!document.getElementById("c-comparador"))
    wrap.innerHTML='<canvas id="c-comparador"></canvas>';
  if(cmpVar==="multidim"){
    document.getElementById("cmp-title").textContent="Perfil multidimensional por ciudad";
    document.getElementById("cmp-lead").textContent="6 dimensiones normalizadas — 0 = mínimo, 100 = máximo entre las 18 ciudades";
    wrap.style.height="460px";
    renderComparadorRadar(S.index.filter(c=>slugs.includes(c.slug)));
    return;
  }
  await Promise.all(slugs.filter(s=>!S.data[s]).map(s=>fetchCityData(s)));
  const cities=slugs.map(s=>S.data[s]).filter(Boolean);if(!cities.length)return;
  wrap.style.height=Math.max(260,cities.length*34+80)+"px";
  document.getElementById("cmp-title").textContent=
    cmpVar==="modal"?"Partición modal por ciudad":
    cmpVar==="proposito"?"Propósito del viaje por ciudad":
    (CMP_IND[cmpIndSel]||{label:cmpIndSel}).label+" por ciudad";
  document.getElementById("cmp-lead").textContent=
    cmpVar==="modal"?"Distribución porcentual del modo de transporte principal":
    cmpVar==="proposito"?"Distribución porcentual del propósito declarado":
    "Comparativa de "+(CMP_IND[cmpIndSel]||{label:""}).label.toLowerCase()+" entre ciudades";
  if(cmpVar==="indicadores"){renderComparadorSimple(cities);return;}
  const isModal=cmpVar==="modal";
  const keys=isModal?["Público","Privado","Caminata","Bicicleta","Combinado","Otro"]:["Trabajo","Estudio","Otro"];
  const cols=isModal?MODO_COL:PROP_COL;
  renderComparadorStacked(
    cities.map(d=>d.ciudad),
    keys.map(k=>({label:k,color:cols[k]||GREY,
      data:cities.map(d=>{
        const arr=isModal?(d.modal||[]):(d.proposito||[]);
        const item=isModal?arr.find(x=>x.modo===k):arr.find(x=>x.prop===k);
        return item?item.pct:0;
      })
    }))
  );
}

const CMP_IND={
  pct_publico:{label:"% Público",fmt:v=>fmt(v,1)+"%",color:NAVY},
  pct_caminata:{label:"% Caminata",fmt:v=>fmt(v,1)+"%",color:GREEN},
  pct_bicicleta:{label:"% Bicicleta",fmt:v=>fmt(v,1)+"%",color:LIME},
  pct_no_motorizado:{label:"% No motorizado",fmt:v=>fmt(v,1)+"%",color:GREEN},
  viajes_persona:{label:"Viajes por persona",fmt:v=>fmt(v,2),color:TEAL},
  dist_mediana:{label:"Dist. mediana (km)",fmt:v=>fmt(v,1)+" km",color:OR},
};

function renderComparadorStacked(cityLabels,datasets){
  const ctx=document.getElementById("c-comparador");if(!ctx)return;
  if(CH["c-comparador"])CH["c-comparador"].destroy();
  CH["c-comparador"]=new Chart(ctx,{
    type:"bar",
    data:{labels:cityLabels,datasets:datasets.map(ds=>({
      label:ds.label,data:ds.data,backgroundColor:ds.color,borderWidth:0
    }))},
    options:{
      indexAxis:"y",maintainAspectRatio:false,
      plugins:{
        legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:8,padding:10,font:{size:11}}},
        datalabels:{
          display:c=>{const v=c.dataset.data[c.dataIndex];return v>=7;},
          anchor:"center",align:"center",color:"#fff",
          font:{size:10,weight:"700"},formatter:v=>v>=7?Math.round(v)+"%":""
        },
        tooltip:{callbacks:{label:c=>c.dataset.label+": "+fmt(c.parsed.x,1)+"%"}}
      },
      scales:{
        x:{stacked:true,display:false,max:100},
        y:{stacked:true,ticks:{font:{size:11}},grid:{display:false}}
      }
    }
  });
}

function renderComparadorSimple(cities){
  const meta=CMP_IND[cmpIndSel];if(!meta)return;
  const ctx=document.getElementById("c-comparador");if(!ctx)return;
  if(CH["c-comparador"])CH["c-comparador"].destroy();
  const vals=cities.map(d=>(d.kpis&&d.kpis[cmpIndSel]!=null)?d.kpis[cmpIndSel]:null);
  const maxVal=Math.max(...vals.filter(v=>v!=null))||1;
  const activeSlug=S.sel?S.sel.slug:null;
  CH["c-comparador"]=new Chart(ctx,{
    type:"bar",
    data:{labels:cities.map(d=>d.ciudad),datasets:[{
      data:vals,borderWidth:0,borderRadius:4,
      backgroundColor:cities.map(d=>d.slug===activeSlug?OR:meta.color)
    }]},
    options:{
      indexAxis:"y",maintainAspectRatio:false,
      layout:{padding:{right:70}},
      plugins:{
        legend:{display:false},
        datalabels:{
          display:true,anchor:"end",align:"end",clamp:true,
          color:isDark()?"#8b949e":"#64748b",
          font:{size:10,weight:"700"},formatter:v=>v!=null?meta.fmt(v):""
        },
        tooltip:{callbacks:{label:c=>meta.fmt(c.parsed.x)}}
      },
      scales:{
        x:{display:false,max:maxVal*1.22},
        y:{ticks:{font:{size:11}},grid:{display:false}}
      }
    }
  });
}

const RADAR_DIMS=[
  {key:"pct_publico",      label:"% Público",    hi:true,  fmt:v=>fmt(v,1)+"%"},
  {key:"pct_no_motorizado",label:"% No motor.",  hi:true,  fmt:v=>fmt(v,1)+"%"},
  {key:"viajes_persona",   label:"V/persona",    hi:true,  fmt:v=>fmt(v,2)},
  {key:"dist_mediana",     label:"Compacidad",   hi:false, fmt:v=>fmt(v,1)+" km"},
  {key:"tiempo_medio_min", label:"Rapidez",      hi:false, fmt:v=>fmt(v,0)+" min"},
  {key:"pct_trabajo",      label:"% Trabajo",    hi:true,  fmt:v=>fmt(v,1)+"%"},
];

function renderComparadorRadar(cities){
  const ctx=document.getElementById("c-comparador");if(!ctx)return;
  if(CH["c-comparador"])CH["c-comparador"].destroy();
  const dimStats=RADAR_DIMS.map(d=>{
    const vals=S.index.map(c=>c[d.key]).filter(v=>v!=null);
    return {mn:Math.min(...vals),mx:Math.max(...vals)};
  });
  const PALETTE=[NAVY,OR,GREEN,TEAL,RED,"#8b5cf6","#ec4899"];
  const dk=isDark();
  const gridClr=dk?"rgba(48,54,61,.8)":"rgba(0,0,0,.1)";
  const lblClr=dk?"#c9d1d9":"#334155";
  CH["c-comparador"]=new Chart(ctx,{
    type:"radar",
    data:{
      labels:RADAR_DIMS.map(d=>d.label),
      datasets:cities.map((city,i)=>({
        label:city.ciudad,
        data:RADAR_DIMS.map((d,j)=>{
          const v=city[d.key];if(v==null)return null;
          const {mn,mx}=dimStats[j];
          const pct=mx===mn?50:(v-mn)/(mx-mn)*100;
          return Math.round(d.hi?pct:100-pct);
        }),
        backgroundColor:PALETTE[i%PALETTE.length]+"28",
        borderColor:PALETTE[i%PALETTE.length],
        borderWidth:2,pointRadius:4,pointHoverRadius:7,
      }))
    },
    options:{
      maintainAspectRatio:false,
      scales:{r:{
        min:0,max:100,
        ticks:{display:false,stepSize:25},
        pointLabels:{font:{size:12,weight:"700"},color:lblClr},
        grid:{color:gridClr},
        angleLines:{color:gridClr},
      }},
      plugins:{
        legend:{display:true,position:"bottom",
          labels:{usePointStyle:true,boxWidth:8,padding:10,font:{size:11}}},
        datalabels:{display:false},
        tooltip:{callbacks:{
          title:items=>"Dimensión: "+items[0].label,
          label:c=>{
            const d=RADAR_DIMS[c.dataIndex];
            const raw=cities[c.datasetIndex]?.[d.key];
            const hint=d.hi?"↑ mejor":"↓ mejor";
            return " "+c.dataset.label+": "+(raw!=null?d.fmt(raw):"s/d")
              +" (score "+c.parsed.r+" · "+hint+")";
          }
        }}
      }
    }
  });
}

// ── Ranking ───────────────────────────────────────────────────────────────────
const RANK_IND={
  pct_publico:{label:"% Transporte público",fmt:v=>fmt(v,1)+"%",color:NAVY},
  pct_no_motorizado:{label:"% No motorizado",fmt:v=>fmt(v,1)+"%",color:GREEN},
  pct_caminata:{label:"% Caminata",fmt:v=>fmt(v,1)+"%",color:GREEN},
  pct_bicicleta:{label:"% Bicicleta",fmt:v=>fmt(v,1)+"%",color:LIME},
  pct_privado:{label:"% Transporte privado",fmt:v=>fmt(v,1)+"%",color:RED},
  viajes_persona:{label:"Viajes por persona",fmt:v=>fmt(v,2),color:TEAL},
  dist_mediana:{label:"Distancia mediana (km)",fmt:v=>fmt(v,1)+" km",color:OR},
  viajes:{label:"Viajes/día (total)",fmt:v=>fmtM(v),color:NAVY2},
};

function renderRanking(){
  if(!S.index.length)return;
  const sel=document.getElementById("rank-ind");
  const asc=document.getElementById("rank-asc");
  if(sel&&!sel._ri){
    sel._ri=true;
    sel.onchange=()=>{rankInd=sel.value;_updateRankTitle();renderRankingChart();};
    if(asc)asc.onchange=e=>{rankAsc=e.target.checked;_updateRankTitle();renderRankingChart();};
  }
  _updateRankTitle();renderRankingChart();
}

function _updateRankTitle(){
  const meta=RANK_IND[rankInd]||{};
  const h3=document.getElementById("rank-title");
  const p=document.getElementById("rank-lead");
  if(h3)h3.textContent="Ranking: "+(meta.label||rankInd);
  if(p){
    const vals=S.index.map(c=>c[rankInd]).filter(v=>v!=null);
    const prom=vals.length?vals.reduce((a,v)=>a+v,0)/vals.length:null;
    p.textContent="18 ciudades ordenadas de "+(rankAsc?"menor a mayor":"mayor a menor")
      +(prom!=null&&meta.fmt?" · promedio nacional: "+meta.fmt(prom):"")+".";
  }
}

function renderRankingChart(){
  if(!S.index.length)return;
  const meta=RANK_IND[rankInd];if(!meta)return;
  const data=S.index.filter(c=>c[rankInd]!=null)
    .map(c=>({label:c.ciudad,value:c[rankInd],slug:c.slug}))
    .sort((a,b)=>rankAsc?a.value-b.value:b.value-a.value);
  if(!data.length)return;
  const wrap=document.getElementById("rank-cwrap");
  if(wrap)wrap.style.height=Math.max(400,data.length*34+80)+"px";
  if(CH["c-ranking"])CH["c-ranking"].destroy();
  const ctx=document.getElementById("c-ranking");if(!ctx)return;
  const maxVal=Math.max(...data.map(d=>d.value));
  const activeSlug=S.sel?S.sel.slug:null;
  CH["c-ranking"]=new Chart(ctx,{
    type:"bar",
    data:{
      labels:data.map(d=>d.label),
      datasets:[{
        data:data.map(d=>d.value),borderWidth:0,borderRadius:4,
        backgroundColor:data.map(d=>d.slug===activeSlug?OR:meta.color)
      }]
    },
    options:{
      indexAxis:"y",maintainAspectRatio:false,
      layout:{padding:{right:72}},
      plugins:{
        legend:{display:false},
        datalabels:{
          display:true,anchor:"end",align:"end",clamp:true,
          color:isDark()?"#8b949e":"#64748b",
          font:{size:11,weight:"700"},formatter:v=>meta.fmt(v)
        },
        tooltip:{callbacks:{label:c=>meta.fmt(c.parsed.x)}}
      },
      scales:{
        x:{display:false,max:maxVal*1.2},
        y:{ticks:{font:{size:12}},grid:{display:false}}
      }
    }
  });
}

// ── Botón compartir ──────────────────────────────────────────────────────────
const SHARE_SVG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>';
const CHECK_SVG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';

function doShare(){
  try{
    navigator.clipboard.writeText(location.href).then(()=>{
      const bd=document.getElementById("shareBtnD");
      const bm=document.getElementById("shareBtn");
      if(bd){bd.innerHTML=CHECK_SVG;setTimeout(()=>{bd.innerHTML=SHARE_SVG;},1800);}
      if(bm){bm.innerHTML=SHARE_SVG+' ¡Copiado!';setTimeout(()=>{bm.innerHTML=SHARE_SVG+' Compartir vista';},1800);}
    });
  }catch(e){prompt("Copia este enlace:",location.href);}
}

document.getElementById("shareBtn").onclick=doShare;
const _sbd=document.getElementById("shareBtnD");
if(_sbd)_sbd.onclick=doShare;

// ── Timestamp de última actualización ────────────────────────────────────────
(function(){
  const el=document.getElementById("sidebar-ts");if(!el)return;
  try{
    const lm=new Date(document.lastModified);
    const d=lm.toLocaleDateString("es-CL",{day:"2-digit",month:"2-digit",year:"numeric"});
    const h=lm.toLocaleTimeString("es-CL",{hour:"2-digit",minute:"2-digit"});
    el.innerHTML='<b>Actualizado:</b><br>'+d+' '+h;
  }catch(e){el.textContent="—";}
})();

// ── Buscador de ciudades ─────────────────────────────────────────────────────
(function(){
  const inp=document.getElementById("city-search");if(!inp)return;
  inp.addEventListener("input",function(){
    const raw=this.value.trim();
    const q=raw.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");
    document.querySelectorAll("#city-list .city-item").forEach(btn=>{
      const name=btn.querySelector(".cn").textContent
        .toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");
      btn.style.display=(!q||name.includes(q))?"":"none";
    });
  });
  inp.addEventListener("keydown",function(e){
    if(e.key!=="Enter")return;
    const visible=[...document.querySelectorAll("#city-list .city-item")]
      .filter(b=>b.style.display!=="none");
    if(visible.length===1){visible[0].click();this.value="";}
  });
})();

// ── Inicialización ───────────────────────────────────────────────────────────
updateThemeIcon();
document.getElementById("themeToggle").onclick=()=>setTheme(!isDark());
document.getElementById("sidebarToggle").onclick=openSidebarMobile;
document.getElementById("sidebarClose").onclick=closeSidebarMobile;
document.getElementById("sidebarOverlay").onclick=closeSidebarMobile;

getJSON("data/eod/index.json").then(idx=>{
  S.index=idx.ciudades;
  buildSelector();
  applyURL();
  // Render national tab if it starts active
  if(currentTab()==="nacional")renderNacional();
}).catch(e=>{
  console.error("No se pudo cargar el índice EOD:",e);
  const main=document.querySelector("main");
  if(main)main.insertAdjacentHTML("afterbegin",
    '<div class="loading">No se pudieron cargar los datos. Verifica que existe <code>data/eod/index.json</code>.</div>');
});
