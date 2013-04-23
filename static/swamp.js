var subscription;
var name;
var currentData;

window.onbeforeunload = function (evt) {
    $.ajax({cache:false,url : '/status?name='+name+'&status=0', 'type' : 'POST'});    
};

function getInfo(name) {
    console.log('Getting info '+name);
    $("#info").empty();
    $.ajax({cache:false, url: '/info?name='+name, 'type' : 'GET',
	    success: function (data) {
		data = JSON.parse(data);
		$("#info").append("<h1>"+data.name+"</h1>");
		$.each(data.measures, function (i,d) {$("#info").append(d+"<br>");});
	    }
	   });
}

function updateView () {
    console.log("data updated");
    $("#data").empty();
    $("#data").append("<table id='tab'></table>");
    $("#tab").append("<tr><th>Name</th><th>Today</th><th>Week</th><th>All</th><th>Current</th></tr>");
    var table = $("#tab");
    var data = currentData;
    for (var i = 0; i < data.names.length; ++i) {
	table.append('<tr class="' + (data.status[data.names[i]] ? 'active' : 'inactive') + '">' +
	                 '<td class="flip" id="'+data.names[i]+'">'+data.names[i]+'</td>' +
		             '<td>' + data.today[data.names[i]] + '</td>' +
		             '<td>' + data.week[data.names[i]] + '</td>' +
		             '<td>' + data.measures[data.names[i]] + '</td>' + 
		             '<td id="'+data.names[i]+'-current">' + tick2ms(data.current[data.names[i]]) + '</td>' + 
		         '</tr>');
	$("#"+data.names[i]).click((function (j) {return function () { getInfo(currentData.names[j]); };})(i));
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
	console.log(currentData.status[name]);
	if (currentData.status[name] == 0) {
	    console.log("inside");
	    document.getElementById('iswork').checked = false;
	    document.getElementById('nowork').checked = true;
	}
	updateView();
    };
    setInterval(ticker, 1000);
    $("#send").disabled = true;
});
