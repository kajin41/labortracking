/**
 * Created by gmercado on 11/18/2016.
 */
$(".filter").change(function (){
  if (this.val() == "Open"){
      document.getElementsByName("From").style.display = 'none';
  }
}
);