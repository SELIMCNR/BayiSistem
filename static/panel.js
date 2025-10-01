fetch("/admin/data")
  .then(res => res.json())
  .then(data => {
    const basvuruTable = document.getElementById("basvuruTable");
    data.basvurular.forEach(([id, ad, tel, adres, paket, durum]) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${ad}</td>
        <td>${tel}</td>
        <td>${adres}</td>
        <td>${paket}</td>
        <td><span class="badge bg-secondary" id="durum-${id}">${durum}</span></td>
        <td>
          <select class="form-select form-select-sm" onchange="guncelleDurum(${id}, this.value, 'basvuru')">
            <option value="">Durum Seç</option>
            <option value="Bekliyor">Bekliyor</option>
            <option value="Arandı">Arandı</option>
            <option value="Kuruldu">Kuruldu</option>
          </select>
        </td>
      `;
      basvuruTable.appendChild(row);
    });

    const altyapiTable = document.getElementById("altyapiTable");
    data.altyapi.forEach(([id, adres, tarih, durum]) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${adres}</td>
        <td>${tarih}</td>
        <td><span class="badge bg-info" id="altyapi-${id}">${durum}</span></td>
        <td>
          <select class="form-select form-select-sm" onchange="guncelleDurum(${id}, this.value, 'altyapi')">
            <option value="">Durum Seç</option>
            <option value="Bekliyor">Bekliyor</option>
            <option value="Yanıtlandı">Yanıtlandı</option>
            <option value="Yönlendirildi">Yönlendirildi</option>
          </select>
        </td>
      `;
      altyapiTable.appendChild(row);
    });
  });

function guncelleDurum(id, yeniDurum, type) {
  fetch("/admin/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, durum: yeniDurum, type })
  })
    .then(res => res.json())
    .then(() => {
      const badgeId = type === "basvuru" ? `durum-${id}` : `altyapi-${id}`;
      const badge = document.getElementById(badgeId);
      badge.textContent = yeniDurum;
      badge.className = "badge bg-success";
    });
}