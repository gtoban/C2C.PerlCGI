#!/usr/bin/perlml
use strict;
use warnings;

use Date::Calc qw(Days_in_Month Today);
use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use clientManager qw(:Client);
use timeManager qw(:Parts);
use Manager qw(:User);
use htmlManager qw(:elements);

my $cgi = CGI->new;
my $sid = $cgi->cookie('CGISESSID') || $cgi->param('CGISESSID') || undef;
my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});

my $userrights = 0;
my $userid = "";
my $userfirstname = "";
my $userlastname = "";
my $useremail = "";
my $userclientid = "";
if ($session->param("userid"))
{
	$userid = $session->param("userid");
	$userfirstname = $session->param("userfirstname");
	$userlastname = $session->param("userlastname");
	$useremail = $session->param("useremail");
	$userclientid = $session->param("userclientid");
	$userrights = $session->param("userrights");
}else
{
	print $cgi->redirect(-url=>'http://www.c2c-hit.net/c2cmobile/login.cgi');			
}

#initial values
my $message = "";


#test form values and untaint

#--------Search Vars
my @susers;
my @sclientids;
my @sdatetypes;
my $sfromday;
my $sfrommonth;
my $sfromyear;
my $sfromdate;
my $stoday;
my $stomonth;
my $stoyear;
my $stodate;
my $shours;
my $sdescription;
my @sstatuses;
my $scount;
my %criteria;
   #--------Search Sort Vars
my $ssuser;
my $ssclient;
my $ssdatetype;
my $ssdate;
my $sshours;
my $ssstatus;
my $ssuserorder;
my $ssclientorder;
my $ssdatetypeorder;
my $ssdateorder;
my $sshoursorder;
my $ssstatusorder;
my $ssuserdir;
my $ssclientdir;
my $ssdatetypedir;
my $ssdatedir;
my $sshoursdir;
my $ssstatusdir;

my @searchsort;

#---------Time Entry List Vars
my $getmytimes;
my $mytimes;
my $success;
my $query;

#---------Single Edit
my $button;
my $iid;
my $waste;

#--------Single or multiedit
my $result;
my $iidlist = "";



if ($cgi->param('submit') )
{   
   @susers = $cgi->param('suser');
   @sclientids = $cgi->param('sclient');
   @sdatetypes = $cgi->param('sdatetype');
   $sfromday = $cgi->param('sfday');
   $sfrommonth = $cgi->param('sfmonth');
   $sfromyear = $cgi->param('sfyear');
   $stoday = $cgi->param('stday');
   $stomonth = $cgi->param('stmonth');
   $stoyear = $cgi->param('styear');
   $shours = $cgi->param('shour');
   $sdescription = $cgi->param('sdescription');
   @sstatuses = $cgi->param('sstatus');

   $ssuser = $cgi->param('ssuser');
   $ssclient = $cgi->param('ssclient');
   $ssdatetype = $cgi->param('ssdatetype');
   $ssdate = $cgi->param('ssdate');
   $sshours = $cgi->param('sshours');
   $ssstatus = $cgi->param('ssstatus');
   $ssuserorder = $cgi->param('ssuserorder');
   $ssclientorder = $cgi->param('ssclientorder');
   $ssdatetypeorder = $cgi->param('ssdatetypeorder');
   $ssdateorder = $cgi->param('ssdateorder');
   $sshoursorder = $cgi->param('sshoursorder');
   $ssstatusorder = $cgi->param('ssstatusorder');
   $ssuserdir = $cgi->param('ssuserdir');
   $ssclientdir = $cgi->param('ssclientdir');
   $ssdatetypedir = $cgi->param('ssdatetypedir');
   $ssdatedir = $cgi->param('ssdatedir');
   $sshoursdir = $cgi->param('sshoursdir');
   $ssstatusdir = $cgi->param('ssstatusdir');

   if (numWordTest($shours, $sdescription))
   {
		$scount = 0;
		foreach (@susers)
		{
			$criteria{'user'}[$scount] = $_;
			$scount += 1;
		}
		if ($userrights == 2)
		{
			$criteria{'user'}[$scount] = $userid;
		}
		$scount = 0;
		foreach (@sclientids)
		{
			$criteria{'clientid'}[$scount] = $_;
			$scount += 1;
		}
		if ($userrights == 1)
		{
			$criteria{'clientid'}[$scount] = $userclientid;
		}
		
		$scount = 0;
		foreach (@sdatetypes)
		{
			$criteria{'datetype'}[$scount] = $_;
			$scount += 1;
		}		
		if ($sfromday && $sfrommonth && $sfromyear)
		{
			$criteria{'fromdate'} = "$sfromyear-$sfrommonth-$sfromday";	
		}
		if ($stoday && $stomonth && $stoyear)
		{
			$criteria{'todate'} = "$stoyear-$stomonth-$stoday";	
		}
		if ($shours)
		{
			$criteria{'hours'} = $shours;
		}
		if ($sdescription)
		{
			$criteria{'description'} = $sdescription;
		}
		$scount = 0;
		foreach (@sstatuses)
		{
			$criteria{'status'}[$scount] = $_;
			$scount += 1;
		}
		
		#-------SORT SEARCH
		$scount = 0;
		if ($ssuser)
		{
			$searchsort[$scount] = [$ssuserorder, $ssuser, $ssuserdir];
			$scount += 1;
		}
		if ($ssclient)
		{
			$searchsort[$scount] = [$ssclientorder, $ssclient, $ssclientdir];
			$scount += 1;
		}
		if ($ssdatetype)
		{
			$searchsort[$scount] = [$ssdatetypeorder, $ssdatetype, $ssdatetypedir];
			$scount += 1;
		}
		if ($ssdate)
		{			
			$searchsort[$scount] = [$ssdateorder, $ssdate, $ssdatedir];
			$scount += 1;
		}
		if ($sshours)
		{
			$searchsort[$scount] = [$sshoursorder, $sshours, $sshoursdir];
			$scount += 1;
		}
		if ($ssstatus)
		{
			$searchsort[$scount] = [$ssstatusorder, $ssstatus, $ssstatusdir];
			$scount += 1;
		}

     	        $getmytimes = getTimes(\%criteria, \@searchsort);
     	        $success = $getmytimes->[1];
     	        if ($success)
     	        {
     	                $mytimes = $getmytimes->[0];
			$query = $getmytimes->[3];
     	              	$message = "Awesome Dude!! $success: $query";
       	        }else
     	        {
     	             	$message = "There was a problem: $getmytimes->[2] : $getmytimes->[3]";
     	        }
     		#$message = getTimes(\%criteria, \@searchsort);
		
		#my $test = @sstatuses;
		#$message = "<p>" . getTimes(\%criteria) . " -- $test<\p>";		
	
   }else
   {
	$message = "Your hours or description are not the correct format.";
   } 
	      
}elsif($cgi->param('single'))
{
	$button = $cgi->param('single');
	$query = $cgi->param('query');
	($waste, $iid) = split / /, $button;
	$result = updateID($iid);
	
	$message = "<p>$result->[0]</p>";
	$getmytimes = getTimes(\%criteria, \@searchsort, $query);
     	$success = $getmytimes->[1];
     	if ($success)
     	{
		$mytimes = $getmytimes->[0];
		$query = $getmytimes->[3];
     		$message .= "<p>Awesome Dude!! $success $query</p>";
       	}else
     	{
		$message = "There was a problem: $getmytimes->[2]";
     	}
		      
}elsif($cgi->param('multiple'))
{
	$message = "made it";
}

#___________________________________________________________________
#
#
#           BEGIN OF HTML
#
#
#
#					BEGIN OF HTML
#
#___________________________________________________________________
#HTML with FORM

print $cgi->header();
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Time Search Results", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" data-mode=\"reflow\" class=\"movie-list ui-responsive\">\n";
#class=\"ui-content\">\n";
print "<p> $message </p>\n";

if ($userrights == 3)
{
print "              <form method=\"post\"> \n";
print " <input type=\"hidden\" name=\"query\" value=\"$query\">\n";
print "<table data-role=\"table\" class=\"ui-responsive\">\n";
print "      <thead>\n";
print "        <tr>\n";
print "         <th>Username</th>\n";
print "         <th>Client</th>\n";
print "         <th>Date Type</th>\n";
print "         <th>Date</th>\n";
print "         <th>Hours</th>\n";
print "         <th>Description</th>\n";
print "         <th>Status</th>\n";
print "         <th>Edit</th>\n";
print "        </tr>\n";
print "      </thead>\n";
foreach my $time (@{$mytimes})
{

print "        <tr>\n";
print "          <td>\n";
print getMyUsers(0, [$time->{'userid'}], $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyClients(0, [$time->{'clientid'}], $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyDateTypes(0, [$time->{'datetype'}], $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyDates($time->{'timedate'}, $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyHours($time->{'hours'}, $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyDescription($time->{'description'}, $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyStatus(0, [$time->{'status'}], $time->{'timeid'});
print "          </td> ";
print "          <td>\n";
print getMySubmit($time->{'timeid'});		
print "          </td> ";
print "        </tr>";
}#loop end
print "      </tbody>\n";
print "</table>\n";
print "              </form>\n";
                          #
}elsif ($userrights == 2) #          USER RIGHTS = 2
{   
  		          #
print "              <form method=\"post\"> \n";
print " <input type=\"hidden\" name=\"query\" value=\"$query\">\n";
print "<h1>Entered Time</h1>";
print "<table data-role=\"table\" class=\"ui-responsive\">\n";
print "      <thead>\n";
print "        <tr>\n";
print "         <th>Client</th>\n";
print "         <th>Date Type</th>\n";
print "         <th>Date</th>\n";
print "         <th>Hours</th>\n";
print "         <th>Description</th>\n";
print "         <th>Status</th>\n";
print "         <th>Edit</th>\n";
print "        </tr>\n";
print "      </thead>\n";
foreach my $time (@{$mytimes})
{
if ($time->{'status'} == 1)
{ 
print " <input type=\"hidden\" name=\"$time->{'timeid'}" . "user\" value=\"$time->{'userid'}\">\n";
print " <input type=\"hidden\" name=\"$time->{'timeid'}" . "status\" value=\"$time->{'status'}\">\n";
print "        <tr>\n";
print "          <td>\n";
print getMyClients(0, [$time->{'clientid'}], $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyDateTypes(0, [$time->{'datetype'}], $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyDates($time->{'timedate'}, $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyHours($time->{'hours'}, $time->{'timeid'});		
print "          </td> ";
print "          <td>\n";
print getMyDescription($time->{'description'}, $time->{'timeid'});		
print "          </td> ";
#print "          <td>\n";
#print getMyStatusName($time->{'status'});
#print "          </td> ";
print "          <td>\n";
print "<p>" . getMyStatusName($time->{'status'}) . "</p>";
print "          </td> ";
print "          <td>\n";
print getMySubmit($time->{'timeid'});		
print "          </td> ";
print "        </tr>";
#
}#                END STATUS = 1
if ($time->{'status'} == 2)
{
print "        <tr>\n";
print "          <td>\n";
print "<p>" . getMyClientsName($time->{'clientid'}) . "</p>";		
print "          </td> ";
print "          <td>\n";
print "<p>$time->{'datetype'}</p>";		
print "          </td> ";
print "          <td>\n";
print "<p>" . $time->{'timedate'} . "</p>";		
print "          </td> ";
print "          <td>\n";
print "<p>" . $time->{'hours'} . "</p>";		
print "          </td> ";
print "          <td>\n";
print "<p>" . $time->{'description'} . "</p>";;		
print "          </td> ";
print "          <td>\n";
print "<p>" . getMyStatusName($time->{'status'}) . "</p>";
print "          </td> ";
print "          <td>\n";
print "<p>No Update</p>";	
print "          </td> ";
print "        </tr>\n";
}#                       END STATUS 2
}#loop end
print "      </tbody>\n";
print "</table>\n";
print "              </form>\n";

#print "<h1>Completed Time</h1>";
#print "<table data-role=\"table\" class=\"ui-responsive\">\n";
#print "      <thead>\n";
#print "        <tr>\n";
#print "         <th>Client</th>\n";
#print "         <th>Date Type</th>\n";
#print "         <th>Date</th>\n";
#print "         <th>Hours</th>\n";
#print "         <th>Description</th>\n";
#print "        </tr>\n";
#print "      </thead>\n";
#foreach my $time (@{$mytimes})
#{
#if ($time->{'status'} == 1)
#{
#print "        <tr>\n";
#print "          <td>\n";
#print "<p>" . getMyClientsName($time->{'clientid'}) . "</p>";		
#print "          </td> ";
#print "          <td>\n";
#print "<p>$time->{'datetype'}</p>";		
#print "          </td> ";
#print "          <td>\n";
#print "<p>" . $time->{'timedate'} . "</p>";		
#print "          </td> ";
#print "          <td>\n";
#print "<p>" . $time->{'hours'} . "</p>";		
#print "          </td> ";
#print "          <td>\n";
#print "<p>" . $time->{'description'} . "</p>";;		
#print "          </td> ";
#print "        </tr>\n";
#}#                       END STATUS 2
#}#loop end
#print "      </tbody>\n";
#print "</table>\n";


    #
}else#              USER RIGHTS = 1
{    #

print "<table data-role=\"table\" class=\"ui-responsive\">\n";
print "      <thead>\n";
print "        <tr>\n";
print "         <th>Username</th>\n";
print "         <th>Date Type</th>\n";
print "         <th>Date</th>\n";
print "         <th>Hours</th>\n";
print "         <th>Description</th>\n";
print "         <th>Status</th>\n";
print "        </tr>\n";
print "      </thead>\n";
foreach my $time (@{$mytimes})
{
print "        <tr>\n";
print "          <td>\n";
print "<p>" . getMyUsersName($time->{'userid'}) . "</p>";		
print "          </td> ";
print "          <td>\n";
print "<p>$time->{'datetype'}</p>";		
print "          </td> ";
print "          <td>\n";
print "<p>" . $time->{'timedate'} . "</p>";		
print "          </td> ";
print "          <td>\n";
print "<p>" . $time->{'hours'} . "</p>";		
print "          </td> ";
print "          <td>\n";
print "<p>" . $time->{'description'} . "</p>";;		
print "          </td> ";
print "          <td>\n";
print "<p>" . getMyStatusName($time->{'status'}) . "</p>";
print "          </td> ";
print "        </tr>\n";
}#loop end
print "      </tbody>\n";
print "</table>\n";

}


print "</div>\n";




print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();

#___________________________________


#-----------------------------


#                          SUBROUTINES


#-----------------------


#______________________________________

sub getMyUsers
{
	my $multiple = shift;
	my $myuserids = shift;
	my $iid = shift;
	
	my $options;
	my @userlist = getUsers();
	my $count = 0;
	$options = $options . "<option value=\"\"></option>\n";
	if (@{$myuserids})
	{		
		while ($count <= $#userlist)
		{
		
			foreach my $myuserid (@{$myuserids})
			{
				if ($userlist[$count]->{'userid'} == $myuserid)
				{
					$options = $options . "<option value=\"$userlist[$count]->{'userid'}\" selected=\"selected\">$userlist[$count]->{'firstname'} $userlist[$count]->{'lastname'}</option>\n";
				}else
				{
					$options = $options . "<option value=\"$userlist[$count]->{'userid'}\">$userlist[$count]->{'firstname'} $userlist[$count]->{'lastname'}</option>\n";
				}
			}
			$count = $count + 1;
		}
	}else
	{		
		while ($count <= $#userlist)
		{			
			$options = $options . "<option value=\"$userlist[$count]->{'userid'}\">$userlist[$count]->{'firstname'} $userlist[$count]->{'lastname'}</option>\n";		$count = $count + 1;	
		}
	}
	$options = $options .  "   </select>\n";

	if ($multiple)
	{
		return "<select name=\"$iid" . "user\" id=\"$iid" . "user\" data-native-menu=\"false\" data-mini=\"true\" multiple=\"multiple\" size=\"$count\">\n" . $options;
	}else
	{
		return "<select name=\"$iid" . "user\" id=\"$iid" . "user\" >\n" . $options;
	}
}
sub getMyClients
{
	my $multiple = shift;
	my $myclientids = shift;
	my $iid = shift;
	
	my $options;
	my @clientlist = getClients();
	my $count = 0;
	$options = $options . "<option value=\"\"></option>\n";
	if (@{$myclientids})
	{
		while ($count <= $#clientlist)
		{
			foreach my $myclientid (@{$myclientids})
			{
				if ($clientlist[$count]->{'clientid'} == $myclientid)
				{
					$options = $options . "<option value=\"$clientlist[$count]->{'clientid'}\" selected=\"selected\">$clientlist[$count]->{'name'}</option>\n";
				}else
				{
					$options = $options . "<option value=\"$clientlist[$count]->{'clientid'}\">$clientlist[$count]->{'name'}</option>\n";
				}
			}
			$count = $count + 1;
		}
	}else
	{
		while ($count <= $#clientlist)
		{
			$options = $options . "<option value=\"$clientlist[$count]->{'clientid'}\">$clientlist[$count]->{'name'}</option>\n";
			
			$count = $count + 1;
		}
	}
	$options = $options .  "   </select>\n";

	if ($multiple)
	{
		return "<select name=\"$iid" . "client\" id=\"$iid" . "client\" data-native-menu=\"false\" data-mini=\"true\" multiple=\"multiple\" size=\"$count\">\n" . $options;
	}else
	{
		return "<select name=\"$iid" . "client\" id=\"$iid" . "sclient\" >\n" . $options;
	}
}
sub getMyDateTypes
{
	my $multiple = shift;
	my $mydatetypes = shift;
	my $iid = shift;
	
	my $options;
	my $datatypes = getDateTypes();
	my $count = 0;
	if (@{$mydatetypes})
	{
		foreach my $type (@{$datatypes})
		{
			foreach my $datetype (@{$mydatetypes})
			{
				if ($type eq $datetype)
				{
					$options = $options . "<option value=\"$type\" selected=\"selected\">$type</option>\n";
				}else
				{
					$options = $options . "<option value=\"$type\">$type</option>\n";	
				}
			}
			$count += 1;
		}
	}else
	{
		foreach my $type (@{$datatypes})
		{
			$options = $options . "<option value=\"$type\">$type</option>\n";		$count += 1;	
		}		
	}

	$options = $options . "</select>\n";

	if ($multiple)
	{
		return "<select name=\"$iid" . "datetype\" id=\"$iid" . "datetype\" data-native-menu=\"false\" data-mini=\"true\" multiple=\"multiple\" size=\"$count\">\n" . $options;
	}else
	{
		return "<select name=\"$iid" . "datetype\" id=\"$iid" . "datetype\" >\n" . $options;
	}	
}
sub getMyDates
{
	my $mydate = shift;
	my $iid = shift;
	my ($uyear,$umonth,$uday) = split /-/, $mydate;	
	my ($dyear,$month,$day)= Today();
	my $dymin = $dyear - 1;
	my $dymax = $dyear + 1;
	my $dyears = [$dyear, $dymax, $dymin];
	my $options = "";
	my $count;
	#return "<p> Made it </p>";#$uyear/$umonth/$uday  :: $dyear </p>";
$options = $options .  "<fieldset data-role=\"controlgroup\" data-type=\"horizontal\">\n";
#<legend>Horizontal controlgroup, mini sized:</legend>
$options = $options .  "<label for=\"$iid" . "year\">Year</label>\n";
$options = $options .  "<select name=\"$iid" . "year\" id=\"$iid" . "year\">\n";
$options = $options .  "<option value=\"\" ></option>\n";
foreach my $year (@{$dyears})
{
	if ($uyear == $year)
	{
		$options = $options .  "<option value=\"$year\" selected=\"selected\">$year</option>\n";
	}else
	{
		$options = $options .  "<option value=\"$year\">$year</option>\n";
	}
}

$options = $options .  "</select>\n";
$options = $options .  "<label for=\"$iid" . "month\">Month</label>\n";
$options = $options .  "<select name=\"$iid" . "month\" id=\"$iid" . "month\">\n";
$options = $options .  "<option value=\"\"></option>\n";
$count = 1;
while ($count <= 12)
{
	if ($umonth == $count)
	{
		$options = $options .  "<option value=\"$count\" selected=\"selected\">$count</option>\n";
	}else
	{
		$options = $options .  "<option value=\"$count\">$count</option>\n";
	}
	$count += 1;
}
$options = $options .  "</select>\n";
$options = $options .  "<label for=\"$iid" . "day\">Day</label>\n";
$options = $options .  "<select name=\"$iid" . "day\" id=\"$iid" . "day\">\n";
$options = $options .  "<option value=\"\" ></option>\n";
$count = 1;
while ($count <= 31)
{
	if ($uday == $count)
	{
		$options = $options .  "<option value=\"$count\" selected=\"selected\">$count</option>\n";
	}else
	{
		$options = $options .  "<option value=\"$count\">$count</option>\n";
	}
	$count += 1;
}
$options = $options .  "</select>\n";
$options = $options .  "</fieldset>\n";

return $options;
}
sub getMyHours
{
	my $myhours = shift;
	my $iid = shift;
	
	return "<label for=\"$iid" . "hours\" class=\"ui-hidden-accessible\">Hours</label>\n<input type=\"text\" name=\"$iid" . "hours\" id=\"$iid" . "hours\" value=\"$myhours\">"  ;
}
sub getMyDescription
{
	my $mydescription = shift;
	my $iid = shift;
	
	return "<label for=\"$iid" . "description\" class=\"ui-hidden-accessible\">Description</label>\n<input type=\"text\" name=\"$iid" . "description\" id=\"$iid" . "description\" value=\"$mydescription\">"  ;
}
sub getMyStatus
{
	my $multiple = shift;
	my $mystatuses = shift;
	my $iid = shift;
	
	my $options;
	my $statuses = getStatus();
	my @keys = keys %{$statuses};
	my $count = 0;
	if (@{$mystatuses})
	{
		foreach my $key (@keys)
		{		
			foreach my $status (@{$mystatuses})
			{			
				if ($key == $status)
				{
					$options = $options . "<option value=\"$key\" selected=\"selected\">$statuses->{$key}</option>\n";
				}else
				{
					$options = $options . "<option value=\"$key\">$statuses->{$key}</option>\n";	
				}
			}
			$count += 1;
		}
	}else
	{
		foreach my $key (@keys)
		{
			$options = $options . "<option value=\"$key\">$statuses->{$key}</option>\n";
			$count += 1;	
		}		
	}

	$options = $options . "</select>\n";

	if ($multiple)
	{
		return "<select name=\"$iid" . "status\" id=\"$iid" . "status\" data-native-menu=\"false\" data-mini=\"true\" multiple=\"multiple\" size=\"$count\">\n" . $options;
	}else
	{
		return "<select name=\"$iid" . "status\" id=\"$iid" . "status\" >\n" . $options;
	}
}
sub getMySubmit
{
	my $iid = shift;
	return "<input type=\"submit\" name=\"single\" value=\"Update $iid\">\n";
}

sub numWordTest
{
	my $num = shift;
	my $word = shift;
	my $good = 1;
	

	if ($num)
	{
		if (!numberTest($num))
		{
			$good = 0;	
		}
		
	}
	if ($word)
	{
		if (!wordTest($word))
		{
			$good = 0;
		}
	}
	return $good;

}

sub updateID
{
	my $iid = shift;
	my $edittimes;
	my $edithours;
	my $editdesc;
	my $update;# = ["Message", 1];

	$edithours = $cgi->param("$iid" . "hours");
	$editdesc = $cgi->param("$iid" . "description");
	if (numWordTest($edithours, $editdesc))
	{
	
		$edittimes = {
		'timeid' => $iid,
		'userid' => $cgi->param("$iid" . "user"),
		'clientid' => $cgi->param("$iid" . "client"),
		'datetype' => $cgi->param("$iid" . "datetype"),
		'timedate' => $cgi->param("$iid" . "year") . "-" . $cgi->param("$iid" . "month") . "-" . $cgi->param("$iid" . "day"),
		'hours' => "$edithours",
		'description' => "$editdesc",
		'status' => $cgi->param("$iid" . "status"),
		
		};
		$update = addUpdateTime($edittimes);

		#$message = " $edittimes->{'user'} :: $iid :: $query";
		
	}
	return $update;
}

sub getMyStatusName
{
	my $statusid = shift;
	my $status = getStatus($statusid);
	return $status->{$statusid};
	
}

sub getMyClientsName
{
	my $clientid = shift;
	my $client = getClientById($clientid);
	return $client->{'name'};
}

sub getMyUsersName
{
	my $userid = shift;
	my $user = getUserById($userid);
	return "$user->{'firstname'} $user->{'lastname'}";
}

