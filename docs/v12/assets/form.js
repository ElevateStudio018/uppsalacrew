(function () {
  "use strict";
  document.querySelectorAll("form[data-mail]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var rader = [];
      f.querySelectorAll("[data-label]").forEach(function (el) {
        var v = "";
        if (el.tagName === "FIELDSET") { var c = el.querySelector("input:checked"); v = c ? c.value : ""; }
        else { v = (el.value || "").trim(); }
        if (v) rader.push(el.getAttribute("data-label") + ": " + v);
      });
      var amne = f.getAttribute("data-subject");
      var a = f.querySelector("[data-amne]");
      if (a && a.value) amne += " – " + a.value;
      window.location.href = "mailto:" + f.getAttribute("data-mail") + "?subject=" + encodeURIComponent(amne) + "&body=" + encodeURIComponent(rader.join("\n"));
      var s = f.querySelector(".uc-status");
      if (s) s.textContent = "Ditt e-postprogram öppnas med allt ifyllt. Skicka mejlet så är det klart. Händer inget? Mejla " + f.getAttribute("data-mail") + ".";
    });
  });
  var arende = new URLSearchParams(location.search).get("arende");
  var sel = document.getElementById("k-arende");
  if (arende && sel) { for (var i = 0; i < sel.options.length; i++) { if (sel.options[i].value === arende) sel.selectedIndex = i; } }
})();
