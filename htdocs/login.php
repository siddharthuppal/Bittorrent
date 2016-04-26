<?php

require_once ("include/functions.php");
require_once ("include/config.php");

function login() {
?>
<?php
block_begin(LOGIN);
if(!isset ($user))$user="";
?>
<form method="post" action="login.php?returnto=<?php echo urlencode("index.php"); ?>">
<table align="center" class="lista" border="0" cellpadding="10">
<tr><td align="right" class="header"><?php echo USER_NAME;?>:</td><td class="lista"><input type="text" size="40" name="uid" value="<?php $user ?>" maxlength="40" /></td></tr>
<tr><td align="right" class="header"><?php echo USER_PWD;?>:</td><td class="lista"><input type="password" size="40" name="pwd" maxlength="40" /></td></tr>
<tr><td colspan="2"  class="header" align="center"><input type="submit" value="<?php echo FRM_CONFIRM;?>" /></td></tr>
<tr><td colspan="2"  class="header" align="center"><?php echo NEED_COOKIES;?></td></tr>
</table>
</form>
<p align="center">
<a href="account.php"><?php echo ACCOUNT_CREATE ?></a>&nbsp;&nbsp;&nbsp;<a href="recover.php"><?php echo RECOVER_PWD ?></a>
</p>
<?php
block_end();
stdfoot();

}

dbconn();

if (!$CURUSER || $CURUSER["uid"]==1) {
if (isset($_POST["uid"]) && $_POST["uid"])
  $user=$_POST["uid"];
else $user='';
if (isset($_POST["pwd"]) && $_POST["pwd"])
  $pwd=$_POST["pwd"];
else $pwd='';

  if (isset($_POST["uid"]) && isset($_POST["pwd"]))
  {
    $res = mysql_query("SELECT * FROM users WHERE username ='".AddSlashes($user)."'")
        or die(mysql_error());
    $row = mysql_fetch_array($res);

    if (!$row)
        {
        standardheader("Login");
        print("<br /><br /><div align=\"center\"><font size=\"2\" color=\"#FF0000\">".ERR_USERNAME_INCORRECT."</font></div>");
        login();
        }
    elseif (md5($row["random"].$row["password"].$row["random"]) != md5($row["random"].md5($pwd).$row["random"]))
        {
                standardheader("Login");
                print("<br /><br /><div align=\"center\"><font size=\"2\" color=\"#FF0000\">".ERR_PASSWORD_INCORRECT."</font></div>");
                login();
                }
    else
    {
    logincookie($row["id"],md5($row["random"].$row["password"].$row["random"]));
    if (isset($_GET["returnto"]))
       $url=urldecode($_GET["returnto"]);
    else
        $url="index.php";

    redirect($url);
    }
  }
  else
  {
   standardheader("Login");
   login();
   exit;
  }
}
else {

  if (isset($_GET["returnto"]))
     $url=urldecode($_GET["returnto"]);
  else
      $url="index.php";

  redirect($url);
}
?>
