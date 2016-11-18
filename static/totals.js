/**
 * Created by gmercado on 11/18/2016.
 */
$(document).ready(function () {
    $(".filter").change(function (){
      if (this.value == "Open"){
          document.getElementsByName("Fromdiv")[0].style.display = 'none';
          document.getElementsByName("Todiv")[0].style.display = 'none';
      }
      else if (this.value == "Job"){
          document.getElementsByName("From")[0].type = 'date';
          document.getElementsByName("To")[0].type = 'date';
          document.getElementsByName("Fromdiv")[0].style.display = 'block';
          document.getElementsByName("Todiv")[0].style.display = 'block';
      }
      else{
          document.getElementsByName("From")[0].type = 'text';
          document.getElementsByName("To")[0].type = 'text';
          document.getElementsByName("Fromdiv")[0].style.display = 'block';
          document.getElementsByName("Todiv")[0].style.display = 'block';
      }
    }
    );
});