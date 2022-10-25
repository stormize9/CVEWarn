/////////////////////////
/// Page liste Hôte   ///
/////////////////////////
//pie
var ctxP = document.getElementById("my-pie-chart").getContext('2d');
var myPieChart = new Chart(ctxP, {
type: 'pie',
data: {
    labels: [],
    datasets: [{
    data: [],
    backgroundColor: ["#007ED6", "#FF7300", "#FFEC00", "#FF0000", "#7CDDDD"],
    hoverBackgroundColor: ["#007ED6", "#FF7300", "#FFEC00", "#FF0000", "#7CDDDD"]
    }]
},
options: {
    responsive: true
}
});

var oslist = new Map();
document.getElementById("host_list").getElementsByTagName("tr").forEach((ligne) => {
if(ligne.childNodes[5] != undefined){
    var os = ligne.childNodes[5].innerText
    if (oslist.has(os)){
    oslist.set(os,oslist.get(os)+1)
    }
    else {
    oslist.set(os,1)
    }
}
})
oslist.delete('OS')
for (var [key, value] of oslist) {    
myPieChart.data.labels.push(key)
myPieChart.data.datasets[0].data.push(value)
}
myPieChart.update()

function ajout_hote() {
    var xhr = new XMLHttpRequest();
    var url = "/api/v1/newhote";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () { //Appelle une fonction au changement d'état.
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        window.location.href = window.location.href.split("?")[0] += "?result=success";
      }
      else if (this.readyState === XMLHttpRequest.DONE && this.status === 500) {
        window.location.href = window.location.href.split("?")[0] += "?result=error";
      }
    }

    var obj = {};
    var hostname = document.getElementById("hostname").value;
    var random = Math.floor(Math.random() * 99999999999999);
    obj["id_infrastructure"] = "{{id_infrastructure}}";
    obj["IDENTIFIER"] = calcMD5(hostname + "." + random);
    obj["IP"] = document.getElementById("IP").value;
    obj["Hostname"] = hostname;
    obj["OS_ref"] = document.getElementById("os").selectedOptions[0].id.split("_")[1];
    var data = JSON.stringify(obj);
    xhr.send(data);
  }
var btn = document.querySelector('#btn_ajout_hote');
btn.addEventListener('click', ajout_hote);




function ajout_os() {
  var xhr = new XMLHttpRequest();
  var url = "/api/v1/newos";
  xhr.open("POST", url, true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () { //Appelle une fonction au changement d'état.
    if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
      window.location.href = window.location.href.split("?")[0] += "?result=success";
    }
    else if (this.readyState === XMLHttpRequest.DONE && this.status === 500) {
      window.location.href = window.location.href.split("?")[0] += "?result=error";
    }
  }
  var obj = {};
  obj["NomOS"] = document.getElementById("nom_os").value;
  obj["VersionOS"] = document.getElementById("version_os").value;
  var data = JSON.stringify(obj);
  xhr.send(data);
}
var btn1 = document.querySelector('#btn_ajout_os');
btn1.addEventListener('click', ajout_os)

if(findGetParameter("result") == "success"){
    document.getElementById("success-notification-toggle").click()
}
if(findGetParameter("result") == "error"){
    document.getElementById("basic-non-sticky-notification-toggle").click()
}


