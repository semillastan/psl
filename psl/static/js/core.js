var Jackpot = function Jackpot(){
  this.labels = [],
  this.data = [],
  this.today = moment().format("MMDDYYYY"),
  
  this.getData = function getData(dataType){
    var dis = this;
    var apiUrl = '/api/top-ten-codes/';
    if(dataType != "top-10"){
      apiUrl = '/api/low-ten-codes/';
    }
    return $.get(apiUrl + this.today, {}, function(res){
      $.each(res.entries, function(key, value){
        dis.labels.push(value.code);
        dis.data.push(value.bet);
      });
    });
  }
};