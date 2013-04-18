var subscription;
var name;
var currentData;

window.onbeforeunload = function (evt) {
    $.ajax({cache:false,url : '/status?name='+name+'&status=0', 'type' : 'POST'});    
};

function updateView () {
    console.log("data updated");
    $("#data").empty();
    $("#data").append("<table id='tab'></table>");
    $("#tab").append("<tr><th>Name<th>Today<th>All<th>Current");
    var table = $("#tab");
    var data = currentData;
    for (var i = 0; i < data.names.length; ++i) {
	table.append('<tr class="' + (data.status[data.names[i]] ? 'active' : 'inactive') +
		     '"><td>'+data.names[i]+'<td>' +
		     data.today[data.names[i]] + '<td>' +
		     data.measures[data.names[i]] + '<td id="'+data.names[i]+'-current">' +
		     tick2ms(data.current[data.names[i]]));
    }
}

function tick2ms (tick) {
    var mins = Math.floor(tick / 60);
    var secs = tick % 60;
    if (secs < 10) secs = "0" + secs;
    if (mins < 10) mins = "0" + mins;
    return mins + ":" + secs;
}

function ticker () {
    if (currentData !== undefined) {
	for (var i in currentData.names) {
	    var name = currentData.names[i];
	    if (currentData.status[name]) {
		currentData.current[name] += 1;
		$("#"+name+"-current").empty();
		$("#"+name+"-current").append(tick2ms(currentData.current[name]));
	    }
	}
    }
}

document.getElementById("login").addEventListener("submit", function () {
    name = document.getElementById("login").elements["name"].value;
    $.ajax({cache:false,url : '/login?name='+name, 'type' : 'POST'});    
    $("#login").remove();
    $("#login-name").append("Logged in as "+name);
    $("#work").append("    Are you working?\n"+
		      "<form id='work'>"+
		      '<input type="radio" id="iswork"  name="working" value="yes" style="background:green;">Yes</input>'+
		      '<input type="radio" id="nowork"  name="working" value="no" style="background:red;" selected>No</input>'+
		      "</form>");
    document.getElementById("iswork").onclick = function () {
	$.ajax({cache:false,url : '/status?name='+name+'&status=1', 'type' : 'POST'});
    };
    document.getElementById("nowork").onclick = function () {
	$.ajax({cache:false,url : '/status?name='+name+'&status=0', 'type' : 'POST'});
    };
    document.getElementById("nowork").click();
    subscription = new EventSource("/subscribe");
    console.log("subscribed");
    subscription.onmessage = function (msg) {
	currentData = JSON.parse(msg.data);
	// if status gets reset, update controls
	if (currentData.status[name] == 0 && !document.getElementById("nowork").value) {
	    document.getElementById("nowork").click();
	}
	updateView();
    };
    setInterval(ticker, 1000);
    $("#send").disabled = true;
});
