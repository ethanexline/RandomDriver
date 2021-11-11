//Click handler for pass tests
$('#data_table_1').on('click', '#pass', function(){
    var row_id = $(this)[0].getAttribute("value");

    var http = new XMLHttpRequest();
    var url = '/api/pass';
    var params = 'id=' +row_id;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        if(http.readyState == 4 && http.status == 200) {
            makeAPIRequest('api/open', displayOpenTests);
        }
    }
    http.send(params);
});

//Click handler for fail tests
$('#data_table_1').on('click', '#fail', function(){
    var row_id = $(this)[0].getAttribute("value");

    var http = new XMLHttpRequest();
    var url = '/api/fail';
    var params = 'id=' +row_id;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        if(http.readyState == 4 && http.status == 200) {
            makeAPIRequest('api/open', displayOpenTests);
        }
    }
    http.send(params);
});

//Click handler for cancel tests
$('#data_table_1').on('click', '#cancel', function(){
    var row_id = $(this)[0].getAttribute("value");

    var http = new XMLHttpRequest();
    var url = '/api/cancel';
    var params = 'id=' +row_id;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        if(http.readyState == 4 && http.status == 200) {
            makeAPIRequest('api/open', displayOpenTests);
        }
    }
    http.send(params);
});


//Global resize functionality
window.onresize = function(event) {
    $('#data_table_1').dataTable().fnAdjustColumnSizing();

};


function makeAPIRequest(endpoint, callback){
    let request = new XMLHttpRequest();
    request.open("GET", endpoint);
    request.send();
    request.onload = () => {
        console.log(request);
        if(request.status == 200){
            callback(request.response);
        }
        else{
            console.log("ERROR IN API REQUEST!");
        }

    }
}

function displayOpenTests(response){
    $('#data_table_1').DataTable().destroy()
    var table = document.getElementById("open_body");
    table.innerHTML = ""
    var table_string = "";
    var row_count = 1;
    var json_response = JSON.parse(response);
    json_response.forEach(obj => {
            table_string += "<tr value='" + obj.id + "'>"
            +"<th scope='row'>"+ row_count + "</th>"
                +"<td>"+ obj.company + "</td>"
                +"<td>"+ obj.terminal + "</td>"
                +"<td>" + obj.driver_code + "</td>"
                +"<td>" + obj.name + "</td>"
                +"<td>" + obj.test_type + "</td>"
                +"<td>" + obj.date + "</td>"
                +"<td>" + obj.hire_date + "</td>"  
                +"<td style='text-align: center;'><button id='pass' value='" + obj.id + "' class='btn btn-sm btn-success'>Pass</button>"
                +   "<button id='fail' value='" + obj.id + "' class='btn btn-sm btn-danger'>Fail</button>"
                +   "<button id='cancel' value='" + obj.id + "' class='btn btn-sm btn-warning'>Cancel</button>"
                + "</td>"

            +"</tr>";
            row_count++;
    });
    table.innerHTML = table_string;
    
    $('#data_table_1').DataTable(
        {
            "scrollY":"60vh",
            "sScrollX": '100%'
        }
    );
   
}


makeAPIRequest('api/open', displayOpenTests);
