try { await import('./probe.js'); }
catch(error) {
  document.querySelector('#stage').textContent='模块未启动';
  document.querySelector('#failure').textContent=String(error?.message||error);
  document.querySelector('#fallback').hidden=false;
  document.querySelector('#retry').onclick=()=>location.reload();
  window.__reefProbeBootstrapError=String(error?.stack||error);
  console.error(error);
}
