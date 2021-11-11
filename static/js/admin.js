//Global resize functionality
window.onresize = function(event) {
    $('#data_table_3').dataTable().fnAdjustColumnSizing();
    $('#data_table_4').dataTable().fnAdjustColumnSizing();
};

function columnSizeAdjust(){
    setTimeout(function(){ 
        $('#data_table_3').dataTable().fnAdjustColumnSizing();
        $('#data_table_4').dataTable().fnAdjustColumnSizing();
    }, 300);

}


//Click handler for deleting users
$('#data_table_3').on('click', '#delete_user', function(){
    var row_id = $(this)[0].getAttribute("value");

    var http = new XMLHttpRequest();
    var url = '/api/deleteuser';
    var params = 'id=' +row_id;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        console.log(http.readyState + ":" + http.status);

        if(http.readyState == 4 && http.status == 200) {
            makeAPIRequest('api/userlist', displayUsers);
            console.log(1)
        }
        else if(http.readyState == 4 && http.status == 301){
            console.log(2)

            var errorMsg = document.getElementById('error_reason');
            errorMsg.innerHTML = "<b>Reason:</b> Cannot delete current user account.";
            $('#errorModal').modal('show');
        }
    }
    http.send(params);
});

//Click handler for deleting users
$('#data_table_4').on('click', '#remove_excluded', function(){
    var row_id = $(this)[0].getAttribute("value");

    var http = new XMLHttpRequest();
    var url = '/api/excludedriverdelete';
    var params = 'id=' +row_id;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        console.log(http.readyState + ":" + http.status);

        if(http.readyState == 4 && http.status == 200) {
            makeAPIRequest('api/getexcludeddrivers', displayExcludedDrivers);
            console.log(1)
        }
        else if(http.readyState == 4 && http.status == 301){
            console.log(2)

            var errorMsg = document.getElementById('error_reason');
            errorMsg.innerHTML = "<b>Reason:</b> Cannot delete current user account.";
            $('#errorModal').modal('show');
        }
    }
    http.send(params);
});

//run a manual report
function adjustTestPerc(){
    var adj_drug = document.getElementById('adj_drug').value;
    var adj_alcohol = document.getElementById('adj_alcohol').value;

    var http = new XMLHttpRequest();
    var url = '/api/adjusttestperc';
    var params = 'adj_drug=' + adj_drug + '&adj_alcohol=' + adj_alcohol;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        console.log(http.readyState + ":" + http.status);

        if(http.readyState == 4 && http.status == 200) {
            var errorMsg = document.getElementById('success_reason');
            errorMsg.innerHTML = "<b>Reason:</b> Drug or Alcohol percent updated successful.";
            $('#successModal').modal('show');

        }
        else if(http.readyState == 4 && http.status == 301){
            var errorMsg = document.getElementById('error_reason');
            errorMsg.innerHTML = "<b>Reason:</b> Drug or Alcohol percent not updated successful.";
            $('#errorModal').modal('show');
        }
    }
    http.send(params);
}


//run a manual report
function runManualReport(){
    var email = document.getElementById('email').value;
    var company = document.getElementById('company').value;
    var drug_number = document.getElementById('number_drug').value;
    var alcohol_number = document.getElementById('number_alc').value;
    console.log(company)
    if(company != 102 && company != 301){
        var errorMsg = document.getElementById('error_reason');
        errorMsg.innerHTML = "<b>Reason:</b> Company must be 102 or 301.";
        $('#errorModal').modal('show');
        return false;
    }

    var http = new XMLHttpRequest();
    var url = '/api/runmanualreport';
    var params = 'email=' + email + '&company=' + company + '&number_drug=' + drug_number + '&number_alc=' + alcohol_number;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        console.log(http.readyState + ":" + http.status);

        if(http.readyState == 4 && http.status == 200) {
            var errorMsg = document.getElementById('success_reason');
            errorMsg.innerHTML = "<b>Reason:</b> Report ran successfully. Your action has been logged.";
            $('#successModal').modal('show');

        }
        else if(http.readyState == 4 && http.status == 301){
            var errorMsg = document.getElementById('error_reason');
            errorMsg.innerHTML = "<b>Reason:</b> Error running report. Your action has been logged.";
            $('#errorModal').modal('show');
        }
    }
    http.send(params);
}

//add excluded driver function
function addExcludedDriver(){
    var driver_code = document.getElementById('new_excluded').value;
    var http = new XMLHttpRequest();
    var url = '/api/excludedriver';
    var params = 'driver_code=' + driver_code;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        console.log(http.readyState + ":" + http.status);

        if(http.readyState == 4 && http.status == 200) {
            makeAPIRequest('api/getexcludeddrivers', displayExcludedDrivers);
            console.log(1)
        }
        else if(http.readyState == 4 && http.status == 301){
            console.log(2)

            var errorMsg = document.getElementById('error_reason');
            errorMsg.innerHTML = "<b>Reason:</b> Could not add driver. Make sure the driver code is valid in the <b>Innovative System</b>";
            $('#errorModal').modal('show');
            document.getElementById('new_excluded').value = "";
        }
    }
    http.send(params);
}


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

function displayUsers(response){
    $('#data_table_3').DataTable().destroy()
    var table = document.getElementById("users_body");
    table.innerHTML = ""
    var table_string = "";
    var row_count = 1;
    var json_response = JSON.parse(response);
    json_response.forEach(obj => {
            table_string += "<tr value='" + obj.id + "'>"
                +"<th scope='row'>"+ obj.id + "</th>"
                +"<td>"+ obj.username + "</td>"
                +"<td>"+ obj.last_login + "</td>"
                +"<td><button value='" + obj.id + "' id='delete_user' class='btn btn-danger'>Delete</button></td>"
                +"</tr>";
            row_count++;
    });
    table.innerHTML = table_string;
    
    $('#data_table_3').DataTable(
        {
            "scrollY":"50vh",
            "sScrollX": '100%'
        }
    );
   
}


function displayExcludedDrivers(response){
    $('#data_table_4').DataTable().destroy()
    var table = document.getElementById("excluded_body");
    table.innerHTML = ""
    var table_string = "";
    var row_count = 1;
    var json_response = JSON.parse(response);
    json_response.forEach(obj => {
            table_string += "<tr value='" + obj.id + "'>"
                +"<th value='" + obj.id +"' scope='row'>"+ obj.driver_code + "</th>"
                +"<td><button value='" + obj.id +"' id='remove_excluded' class='btn btn-warning'>Remove</button></td>"
                +"</tr>";
            row_count++;
    });
    table.innerHTML = table_string;
    
    $('#data_table_4').DataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bFilter": true,
        "bInfo": false,
        "bAutoWidth": false,
        "scrollY":"20vh",
    });

   
}



makeAPIRequest('api/userlist', displayUsers);
makeAPIRequest('api/getexcludeddrivers', displayExcludedDrivers);
