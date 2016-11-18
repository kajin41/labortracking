/**
 * Created by gmercado on 11/18/2016.
 */
$(document).ready(function () {
    $(".filter").change(function (){
      if (this.value == "Open"){
          document.getElementsByName("From").style.display = 'none';
      }
    }
    );
});