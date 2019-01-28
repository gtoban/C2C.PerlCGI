#!/usr/bin/perlml
use strict;
use warnings;

use Date::Calc qw(Days_in_Month Today);
use DBI;
use CGI::Session;
use CGI;
use Mail::Sendmail;
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

my $entertime;
my $report;
my $message;
my $success = 0;
my $clientid;
my $datetype;
my $hours;
my $description;

#--------Date Vars
my $date;
my ($year, $month, $day)= Today();
my $ymin = $year - 1;
my $ymax = $year + 1;

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

#---------Time Entry List Vars
my $pretest;
my $mytimes;



if ($cgi->param('nosubmit') )
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

   $ssuser = cgi->param('ssuser');
   $ssclient = cgi->param('ssclient');
   $ssdatetype = cgi->param('ssdatetype');
   $ssdate = cgi->param('ssdate');
   $sshours = cgi->param('sshours');
   $ssstatus = cgi->param('ssstatus');
   $ssuserorder = cgi->param('ssuserorder');
   $ssclientorder = cgi->param('ssclientorder');
   $ssdatetypeorder = cgi->param('ssdatetypeorder');
   $ssdateorder = cgi->param('ssdateorder');
   $sshoursorder = cgi->param('sshoursorder');
   $ssstatusorder = cgi->param('ssstatusorder');
   $ssuserdir = cgi->param('ssuserdir');
   $ssclientdir = cgi->param('ssclientdir');
   $ssdatetypedir = cgi->param('ssdatetypedir');
   $ssdatedir = cgi->param('ssdatedir');
   $sshoursdir = cgi->param('sshoursdir');
   $ssstatusdir = cgi->param('ssstatusdir');

   $message = "<p>Users</p>";
   foreach (@susers)
   {
	$message = $message . "<p>$_</p>";
   }
   $message = $message . "<p>Clients</p>";
   foreach (@sclientids)
   {
	$message = $message . "<p>$_</p>";
   }
   $message = $message . "<p>Date Types</p>";
   foreach (@sdatetypes)
   {
	$message = $message . "<p>$_</p>";
   }
   $message = $message . "<p>From Year</p>";
   $message = $message . "<p>$sfromyear - $sfrommonth - $sfromday</p>";
   $message = $message . "<p>To Year</p>";
   $message = $message . "<p>$stoyear - $stomonth - $stoday</p>";
   $message = $message . "<p>Hours</p>";
   $message = $message . "<p>$shours</p>";
   $message = $message . "<p>Description</p>";
   $message = $message . "<p>$sdescription</p>";
   $message = $message . "<p>Status</p>";
   foreach (@sstatuses)
   {
	$message = $message . "<p>$_</p>";
   }

   if (numWordTest($shours, $sdescription))
   {
		$scount = 0;
		foreach (@susers)
		{
			$criteria{'user'}[$scount] = $_;
			$scount += 1;
		}
		$scount = 0;
		foreach (@sclientids)
		{
			$criteria{'clientid'}[$scount] = $_;
			$scount += 1;
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
		foreach (@sstatuses)
		{
			$criteria{'status'}[$scount] = $_;
			$scount += 1;
		}

		#$mytimes = getTimes(\%criteria);
		#$message = "<p>" . getTimes(\%criteria) . "<\p>";		
	
   }else
   {
	$message = "Your hours or description are not the correct format.";
   }
   if (0)#numberTest($year) && numberTest($month) && numberTest($day))
   {
	
	if ( $year > $ymax || $year < $ymin)
	{
		$message = "Year is bad.";
	}elsif ( $month > 12 || $month < 1)
	{
		$message = "Month is bad.";
	}elsif ( $day > 31 || $day < 1)
	{
		$message = "Day is bad.";
	}else
	{
		$clientid = $cgi->param('client');
		$datetype = $cgi->param('datetype');
		$date = "$year-$month-$day";
		$hours = $cgi->param('hours');
		$description = $cgi->param('description');
		
		$entertime = {
		'userid' => $userid,
		'clientid' => $clientid,
		'datetype' => $datetype,
		'date' => $date,
		'hours' => $hours,
		'description' => $description,
		'statusid' => 1,
		};
		
		$report = addUpdateTime($entertime);
		$message = $report->[0];
		
		if ($report->[1])
		{
			$clientid = "";
			$datetype = "";
			($year, $month, $day)= Today();
			$year = $year + 1900;
			$hours = "";
			$description = "";
		}
   	}
   }else
   {
	#$message = "Your date must be a number";
   }
   
	      
}

#HTML with FORM
print $cgi->header();

print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Enter Time", 1, $userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
print "ClientId = $userclientid";
if (!$success)
{
print "<p>You can limit results by setting your search criteria here.</p>";
print "<form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/time/timesearchresult.cgi\">\n";

if ($userrights == 3)
{
print "   <label for=\"suser\">User(s)</label>\n";
print 	  getMyUsers(1, \@susers, "s");
}elsif ($userrights == 2)
{
print "<input type=\"hidden\" name=\"suser\" value=\"$userid\"/>";
}

if ($userrights == 1)
{
print "<input type=\"hidden\" name=\"sclient\" value=\"$userclientid\"/>";
}else
{
print "   <label for=\"sclient\">Client(s)</label>\n";
print 	  getMyClients(1, \@sclientids, "s");
}

print "   <label for=\"sdatetype\">Date Type</label>\n";
print 	  getMyDateTypes(1, \@sdatetypes, "s");

print "<p>From Date: Year Month Day</p>\n";
print "<p>The target date is greater than or equal to:</p>";
print getMyDate($ymin, $ymax, $sfromyear, $sfrommonth, $sfromday, "sf");

print "<p>To Date: Year Month Day</p>\n";
print "<p>The target date is less than or equal to:</p>";
print getMyDate($ymin, $ymax, $stoyear, $stomonth, $stoday, "st");

print "   <label for=\"shour\">Hours</label>\n";
print "	  <input type=\"textfield\" name=\"shour\" id=\"shour\" value=\"$shours\">\n";

print "<p>The description \"Contains\":</p>";
print " 	<label for=\"sdescription\">Description</label>\n";
print " 	<textarea cols=\"40\" rows=\"8\" name=\"sdescription\" id=\"sdescription\">$sdescription</textarea>\n";

if (0)#$userrights == 2)
{
print "   <label for=\"sstatus\">Status</label>\n";
print 	  getMyStatus(0, \@sstatuses, "s");
}else
{
print "   <label for=\"sstatus\">Status</label>\n";
print 	  getMyStatus(1, \@sstatuses, "s");
}

print "<h3>Sort By</h3>";

print "<div class=\"ui-grid-b\">\n";

print "	<div class=\"ui-block-a\">\n";
print "<fieldset data-role=\"controlgroup\">\n";
print "<legend>Columns</legend>\n";
print "<input type=\"checkbox\" name=\"ssuser\" id=\"ssuser\" value=\"user\">\n";
print "<label for=\"ssuser\">User</label>\n";
print "<input type=\"checkbox\" name=\"ssclient\" id=\"ssclient\" value=\"client\">\n";
print "<label for=\"ssclient\">Client</label>\n";
print "<input type=\"checkbox\" name=\"ssdatetype\" id=\"ssdatetype\" value=\"datetype\">\n";
print "<label for=\"ssdatetype\">Date Type</label>\n";
print "<input type=\"checkbox\" name=\"ssdate\" id=\"ssdate\" value=\"date\">\n";
print "<label for=\"ssdate\">Date</label>\n";
print "<input type=\"checkbox\" name=\"sshours\" id=\"sshours\" value=\"hours\">\n";
print "<label for=\"sshours\">Hours</label>\n";
print "<input type=\"checkbox\" name=\"ssstatus\" id=\"ssstatus\" value=\"status\">\n";
print "<label for=\"ssstatus\">Status</label>\n";
print "</fieldset>\n";
print " </div>\n";

print " <div class=\"ui-block-b\">\n";
print "	<fieldset data-role=\"controlgroup\">                \n";
print "	<legend>Sort Order</legend>              \n";
print "	<label for=\"ssuserorder\">User</label>	     \n";
print "	<select name=\"ssuserorder\" id=\"ssuserorder\"> \n";
print "	<option value=\"1\">One</option>			     \n";
print "	<option value=\"2\">Two</option>			     \n";
print "	<option value=\"3\">Three</option>		     \n";
print "	<option value=\"4\">Four</option>			     \n";
print "	<option value=\"5\">Five</option>			     \n";
print "	<option value=\"6\">Six</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"ssclientorder\">Client</label>	     \n";
print "	<select name=\"ssclientorder\" id=\"ssclientorder\"> \n";
print "	<option value=\"1\">One</option>			     \n";
print "	<option value=\"2\">Two</option>			     \n";
print "	<option value=\"3\">Three</option>		     \n";
print "	<option value=\"4\">Four</option>			     \n";
print "	<option value=\"5\">Five</option>			     \n";
print "	<option value=\"6\">Six</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"ssdatetypeorder\">Date Type</label>	     \n";
print "	<select name=\"ssdatetypeorder\" id=\"ssdatetypeorder\"> \n";
print "	<option value=\"1\">One</option>			     \n";
print "	<option value=\"2\">Two</option>			     \n";
print "	<option value=\"3\">Three</option>		     \n";
print "	<option value=\"4\">Four</option>			     \n";
print "	<option value=\"5\">Five</option>			     \n";
print "	<option value=\"6\">Six</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"ssdateorder\">Date</label>	     \n";
print "	<select name=\"ssdateorder\" id=\"ssdateorder\"> \n";
print "	<option value=\"1\">One</option>			     \n";
print "	<option value=\"2\">Two</option>			     \n";
print "	<option value=\"3\">Three</option>		     \n";
print "	<option value=\"4\">Four</option>			     \n";
print "	<option value=\"5\">Five</option			     \n";
print "	<option value=\"6\">Six</option>		     \n";
print "	</select>			     \n";
print "	<label for=\"sshoursorder\">Hours</label>	     \n";
print "	<select name=\"sshoursorder\" id=\"sshoursorder\"> \n";
print "	<option value=\"1\">One</option>			     \n";
print "	<option value=\"2\">Two</option>			     \n";
print "	<option value=\"3\">Three</option>		     \n";
print "	<option value=\"4\">Four</option>			     \n";
print "	<option value=\"5\">Five</option>			     \n";
print "	<option value=\"6\">Six</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"ssstatusorder\">Status</label>	     \n";
print "	<select name=\"ssstatusorder\" id=\"ssstatusorder\"> \n";
print "	<option value=\"1\">One</option>			     \n";
print "	<option value=\"2\">Two</option>			     \n";
print "	<option value=\"3\">Three</option>		     \n";
print "	<option value=\"4\">Four</option>			     \n";
print "	<option value=\"5\">Five</option>			     \n";
print "	<option value=\"6\">Six</option>		     \n";
print "	</select>					     \n";
print " </fieldset>                                          \n";
print "	</div>\n";

print " <div class=\"ui-block-c\">\n";
print "	<fieldset data-role=\"controlgroup\">                \n";
print "	<legend>Asc\\Desc</legend>              \n";
print "	<label for=\"ssuserdir\">User</label>	     \n";
print "	<select name=\"ssuserdir\" id=\"ssuserdir\"> \n";
print "	<option value=\"ASC\">Ascending</option>	     \n";
print "	<option value=\"DESC\">Descending</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"ssclientdir\">Client</label>	     \n";
print "	<select name=\"ssclientdir\" id=\"ssclientdir\"> \n";
print "	<option value=\"ASC\">Ascending</option>	     \n";
print "	<option value=\"DESC\">Descending</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"ssdatetypedir\">Date Type</label>	     \n";
print "	<select name=\"ssdatetypedir\" id=\"ssdatetypedir\"> \n";
print "	<option value=\"ASC\">Ascending</option>	     \n";
print "	<option value=\"DESC\">Descending</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"ssdatedir\">Date</label>	     \n";
print "	<select name=\"ssdatedir\" id=\"ssdatedir\"> \n";
print "	<option value=\"ASC\">Ascending</option>	     \n";
print "	<option value=\"DESC\">Descending</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"sshoursdir\">Hours</label>	     \n";
print "	<select name=\"sshoursdir\" id=\"sshoursdir\"> \n";
print "	<option value=\"ASC\">Ascending</option>	     \n";
print "	<option value=\"DESC\">Descending</option>		     \n";
print "	</select>					     \n";
print "	<label for=\"ssstatusdir\">Status</label>	     \n";
print "	<select name=\"ssstatusdir\" id=\"ssstatusdir\"> \n";
print "	<option value=\"ASC\">Ascending</option>	     \n";
print "	<option value=\"DESC\">Descending</option>		     \n";
print "	</select>					     \n";
print " </fieldset>                                          \n";
print "	</div>\n";

print "</div>\n";

print "<input type=\"submit\" name=\"submit\" value=\"submit\">\n";
print "</form>\n";
}
#print "<p>If you have any additional problems please contact Coast to Coast at 865-209-6586.</p>";
print "</div>\n";




print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";


print $cgi->end_html();

#_____________________________________________________________


#--------------------------SUBROUTINES

#______________________________________________________


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

sub getMyDate
{
	my $dymin = shift;
	my $dymax = shift;
	my $uyear = shift;
	my $umonth = shift;
	my $uday = shift;
	my $iid = shift;
	my $dyear = $dymax - 1;
	my $dyears = [$dyear, $dymax, $dymin];
	my $options = "";
	my $count;
	
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

