// UTILITES FUNCTIONS HERE


// to display figures properly
export function formatFigure(figure, significant_digits=null, simplify_figure_inf1=true){
  if (typeof(figure) == "number"){
    if (significant_digits == null){
      return figure.toLocaleString("fr-FR")
    } else {
      if (figure < 1 && simplify_figure_inf1){
        return parseFloat(figure.toPrecision(1)).toLocaleString("fr-FR")
      } else {
        return parseFloat(figure.toPrecision(significant_digits)).toLocaleString("fr-FR")
      }
    }
  }
  else{
    return figure
  }
}

// to display names properly : return string with capital letter for first letter of each word
export function titleCase(str) {
  if (str==null){return str}
   var splitStr = str.toLowerCase().split(' ');
   for (var i = 0; i < splitStr.length; i++) {
       // You do not need to check if i is larger than splitStr length, as your for does that for you
       // Assign it back to the array
       splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);
   }
   // Directly return the joined string
   return splitStr.join(' ');
}

export function downloadBlob(content, filename, contentType){
  // Create a blob
  let blob = new Blob([content], { type: contentType });
  let url = URL.createObjectURL(blob);

  // Create a link to download it
  let a = document.createElement('a');
  a.href = url;
  a.setAttribute('download', filename);
  a.click();
}

export function arrayToCsv(array){
  let csvFormat = array.map(row =>
    row
    .join(';')  // comma-separated
  ).join('\r\n');  // rows starting on new lines
  return csvFormat
}

export function cols_to_rows(cols){
    let rows = [];
    for (let i=0; i<cols[0].length; i++){
      rows.push(cols.map((t) => t[i]))
    }
    return rows
}

export function downloadCSV(headlines, rows, format_csv, name){
  let format_rows = rows.map((row) => row.map((e, i)=> format_csv[i](e)))
  let all_rows = [headlines].concat(format_rows)
  let csv = arrayToCsv(all_rows)
  downloadBlob("\uFEFF" + csv, name + ".csv", "text/csv;charset=utf-8,")
}
