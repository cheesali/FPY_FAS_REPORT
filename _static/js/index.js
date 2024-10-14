// function exportTableToExcel(tableName) {
//   const table = document.getElementById(tableName);
//   if (!table) {
//     console.error(`Таблица с ID '${tableName}' не найдена.`);
//     return;
//   }

//   const data = [];

//   // Получаем заголовки таблицы
//   const headerRow = table.querySelector("thead tr");
//   const headerCells = headerRow.querySelectorAll("th");
//   const headerData = Array.from(headerCells).map((cell) => cell.textContent);
//   data.push(headerData);

//   // Получите строки с данными
//   const rows = table.querySelectorAll("tbody tr"); // Измените селектор
//   rows.forEach((row) => {
//     const cells = row.querySelectorAll("td");
//     const rowData = Array.from(cells).map((cell) =>
//       cell.textContent.replace(/\./g, ",")
//     );
//     data.push(rowData);
//   });

//   // Определяем имя файла в зависимости от title страницы
//   const title = document.title;
//   const filename = `${title}.xlsx`;

//   const workbook = XLSX.utils.book_new();
//   const worksheet = XLSX.utils.aoa_to_sheet(data);
//   XLSX.utils.book_append_sheet(workbook, worksheet, "Data");

//   XLSX.writeFile(workbook, filename);
// }

// window.onload = function () {
//   // document.body.style.zoom = 0.9;
//   const exportButton = document.getElementById("export_Button");
//   if (exportButton) {
//     exportButton.addEventListener("click", function () {
//       let tableName = "";
//       const table = document.querySelector("table");
//       if (table) {
//         tableName = table.id;
//         exportTableToExcel(tableName);
//       }
//     });
//   }
// };
