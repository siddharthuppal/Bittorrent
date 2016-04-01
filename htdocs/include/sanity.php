<?php

function do_sanity() {

         global $PRIVATE_ANNOUNCE, $TORRENTSDIR, $CURRENTPATH,$LIVESTATS,$LOG_HISTORY;

         // SANITY FOR TORRENTS
         $results = mysql_query("SELECT summary.info_hash, seeds, leechers, dlbytes, namemap.filename FROM summary LEFT JOIN namemap ON summary.info_hash = namemap.info_hash WHERE namemap.external='no'");
         $i = 0;
         while ($row = mysql_fetch_row($results))
         {
             list($hash, $seeders, $leechers, $bytes, $filename) = $row;

         $timeout=time()-intval($GLOBALS["report_interval"]);

         // for testing purpose -- begin
         $resupd=mysql_query("SELECT * FROM peers where lastupdate < ".$timeout ." AND infohash='$hash'");
         if (mysql_num_rows($resupd)>0)
            {
            while ($resupdate = mysql_fetch_array($resupd))
              {
                  $uploaded=max(0,$resupdate["uploaded"]);
                  $downloaded=max(0,$resupdate["downloaded"]);
                  $pid=$resupdate["pid"];
                  $ip=$resupdate["ip"];
                  // update user->peer stats only if not livestat
                  if (!$LIVESTATS)
                    {
                      if ($PRIVATE_ANNOUNCE)
                         quickQuery("UPDATE users SET uploaded=uploaded+$uploaded, downloaded=downloaded+$downloaded WHERE pid='$pid' AND id>1 LIMIT 1");
                      else // ip
                          quickQuery("UPDATE users SET uploaded=uploaded+$uploaded, downloaded=downloaded+$downloaded WHERE cip='$ip' AND id>1 LIMIT 1");
                     }

                  // update dead peer to non active in history table
                  if ($LOG_HISTORY)
                     {
                          $resuser=mysql_query("SELECT id FROM users WHERE ".($PRIVATE_ANNOUNCE?"pid='$pid'":"cip='$ip'")." ORDER BY lastconnect DESC LIMIT 1");
                          $curu=@mysql_fetch_row($resuser);
                          quickquery("UPDATE history SET active='no' WHERE uid=$curu[0] AND infohash='$hash'");
                     }

            }
         }
         // for testing purpose -- end

            quickQuery("DELETE FROM peers where lastupdate < ".$timeout." AND infohash='$hash'");
            quickQuery("UPDATE summary SET lastcycle='".time()."' WHERE info_hash='$hash'");

             $results2 = mysql_query("SELECT status, COUNT(status) from peers WHERE infohash='$hash' GROUP BY status");
             $counts = array();
             while ($row = mysql_fetch_row($results2))
                 $counts[$row[0]] = 0+$row[1];

             quickQuery("UPDATE summary SET leechers=".(isset($counts["leecher"])?$counts["leecher"]:0).",seeds=".(isset($counts["seeder"])?$counts["seeder"]:0)." WHERE info_hash=\"$hash\"");
             if ($bytes < 0)
             {
                 quickQuery("UPDATE summary SET dlbytes=0 WHERE info_hash=\"$hash\"");
             }

         }
         // END TORRENT'S SANITY

         //  optimize peers table
         quickQuery("OPTIMIZE TABLE peers");

		 // delete readposts when topic don't exist or deleted  *** should be done by delete, just in case
		 quickQuery("DELETE readposts FROM readposts LEFT JOIN topics ON readposts.topicid = topics.id WHERE topics.id IS NULL");
		 
		 // delete readposts when users was deleted *** should be done by delete, just in case
		 quickQuery("DELETE readposts FROM readposts LEFT JOIN users ON readposts.userid = users.id WHERE users.id IS NULL");
		 
         // deleting orphan image in torrent's folder (if image code is enabled)
         $tordir=realpath("$CURRENTPATH/../$TORRENTSDIR");
         if ($dir = @opendir($tordir."/"));
           {
            while(false !== ($file = @readdir($dir)))
               {
                   if ($ext = substr(strrchr($file, "."), 1)=="png")
                       unlink("$tordir/$file");
               }
            @closedir($dir);
         }

}
?>
