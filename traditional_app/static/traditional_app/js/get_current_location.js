document.addEventListener("DOMContentLoaded", function () {
  const lonField = document.getElementById("id_longitude");
  const latField = document.getElementById("id_latitude");

  if (!lonField || !latField || lonField.value || latField.value) return;

  // Make fields readonly at first
  lonField.readOnly = true;
  latField.readOnly = true;

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        const lon = pos.coords.longitude;
        const lat = pos.coords.latitude;

        // Fill values if empty
        if (!lonField.value && !latField.value) {
          lonField.value = lon.toFixed(6);
          latField.value = lat.toFixed(6);

        // Now allow editing
        lonField.readOnly = false;
        latField.readOnly = false;
        }

      },
      function (err) {
        console.warn("Geolocation error:", err);

        // If user denies, still allow manual editing
        lonField.readOnly = false;
        latField.readOnly = false;
      }
    );
  } else {
    // Geolocation not supported → allow manual editing
    lonField.readOnly = false;
    latField.readOnly = false;
  }
});
