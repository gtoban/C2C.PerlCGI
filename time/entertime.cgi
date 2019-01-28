#!/usr/bin/perlml
use strict;
use warnings;

use Time::localtime;
use DBI;
use CGI::Session;
use CGI;
use Mail::Sendmail;
use lib '/home/c2cmedical/public_html/c2c/modules';
use clientManager qw(:Client);
use timeManager qw(:Parts);
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
my $date;
my $tm;
my $entertime;
my $report;
my $message;
my $success = 0;
my $clientid;
my $datetype;
my $hours;
my $description;

$tm = localtime;
my ($day,$month,$year)=($tm->mday, $tm->mon, $tm->year);
$year = $year + 1900;
my $ymin = $year - 1;
my $ymax = $year + 1;


if ($cgi->param('submit') )
{
   $day = $cgi->param('day');
   $month = $cgi->param('month');
   $year = $cgi->param('year');
   if (numberTest($year) && numberTest($month) && numberTest($day))
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
			($day,$month,$year)=($tm->mday, $tm->mon, $tm->year);
			$year = $year + 1900;
			$hours = "";
			$description = "";
		}
   	}
   }else
   {
	$message = "Your date must be a number";
   }
	      
}

#HTML with FORM
print $cgi->header();

print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Enter Time", 1, $userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
print $message;
if (!$success)
{
print "<p>Please enter your information.</p>";
print "<form method=\"post\">\n";
print "<input type=\"hidden\" name=\"userid\" value=\"$userid\">\n";
print "   <label for=\"client\">Client</label>\n";
print "	  <select name=\"client\" id=\"client\">\n";
print "   <option value=\"\"></option>\n";
print 	  getMyClients();
print "   </select>\n";
print "   <label for=\"datetype\">Date Type</label>\n";
print "	  <select name=\"datetype\" id=\"datetype\">\n";
print 	  getMyDateTypes();
print "   </select>\n";

print "<p>Date: Year Month Day</p>\n";
print getMyDate($ymin, $ymax, $year, $month, $day);

print "   <label for=\"hours\">Hours</label>\n";
print "	  <input type=\"textfield\" name=\"hours\" id=\"hours\" value=\"$hours\">\n";

print " 	<label for=\"description\">Description</label>\n";
print " 	<textarea cols=\"40\" rows=\"8\" name=\"description\" id=\"description\">$description</textarea>\n";

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


sub getMyClients
{
	
	my $options;
	my @clientlist = getClients();
	my $count = 0;
	while ($count <= $#clientlist)	
#	foreach my $client (@clientlist)
	{
		if ($clientlist[$count]->{'clientid'} == $clientid)
		{
			$options = $options . "<option value=\"$clientlist[$count]->{'clientid'}\" selected>$clientlist[$count]->{'name'}</option>\n";
		}else
		{
			$options = $options . "<option value=\"$clientlist[$count]->{'clientid'}\">$clientlist[$count]->{'name'}</option>\n";
		}
		$count = $count + 1;
	}
	return $options;
	
}

sub getMyDateTypes
{
	my $options;
	my $datatypes = getDateTypes();
	
	foreach my $type (@{$datatypes})
	{
		if ($type eq $datetype)
		{
			$options = $options . "<option value=\"$type\" selected>$type</option>\n";
		}else
		{
			$options = $options . "<option value=\"$type\">$type</option>\n";	
		}
	}
	return $options;
}

sub getMyDate
{
	my $dymin = shift;
	my $dymax = shift;
	my $uyear = shift;
	my $umonth = shift;
	my $uday = shift;
	my $dyear = $dymax - 1;
	my $dyears = [$dyear, $dymax, $dymin];
	my $options = "";
	my $count;
	
$options = $options .  "<fieldset data-role=\"controlgroup\" data-type=\"horizontal\">\n";
#<legend>Horizontal controlgroup, mini sized:</legend>
$options = $options .  "<label for=\"year\">Year</label>\n";
$options = $options .  "<select name=\"year\" id=\"year\">\n";
foreach my $year (@{$dyears})
{
	if ($uyear == $year)
	{
		$options = $options .  "<option value=\"$year\" selected>$year</option>\n";
	}else
	{
		$options = $options .  "<option value=\"$year\">$year</option>\n";
	}
}

$options = $options .  "</select>\n";
$options = $options .  "<label for=\"month\">Month</label>\n";
$options = $options .  "<select name=\"month\" id=\"month\">\n";
$count = 1;
while ($count <= 12)
{
	if ($umonth == $count)
	{
		$options = $options .  "<option value=\"$count\" selected>$count</option>\n";
	}else
	{
		$options = $options .  "<option value=\"$count\">$count</option>\n";
	}
	$count += 1;
}
$options = $options .  "</select>\n";
$options = $options .  "<label for=\"day\">Day</label>\n";
$options = $options .  "<select name=\"day\" id=\"day\">\n";
$count = 1;
while ($count <= 31)
{
	if ($uday == $count)
	{
		$options = $options .  "<option value=\"$count\" selected>$count</option>\n";
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

