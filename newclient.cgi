#!/usr/bin/perl
use cPanelUserConfig;
use strict;
use warnings;

use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use clientManager qw(:Client :Clientcheck :Clientedit);
use htmlManager qw(:elements);

my $cgi = CGI->new;
my $sid = $cgi->cookie('CGISESSID') || $cgi->param('CGISESSID') || undef;
my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});

#my $userid = $session->param("userid");
my $userrights = 0;
if ($session->param("userid"))
{
	my $userid = $session->param("userid");
	my $userfirstname = $session->param("userfirstname");
	my $userlastname = $session->param("userlastname");
	my $useremail = $session->param("useremail");
	my $userclientid = $session->param("userclientid");
	$userrights = $session->param("userrights");
}else
{
	print $cgi->redirect(-url=>'http://www.c2c-hit.net/c2cmobile/login.cgi');			
}

my $updateclient;
my $message = "";
my $tempdate;
if ($cgi->param('submit'))
{
    $tempdate = $cgi->param('yearstartdate') . "-" . $cgi->param('monthstartdate') . "-" . $cgi->param('daystartdate');
    $updateclient = {
	'name' => $cgi->param('name'),
	'schedule' => $cgi->param('schedule'),
	'startdate' => $tempdate,
	'dayofweek' => $cgi->param('dayofweek')
    };
    $message = addUpdateClient($updateclient);
    #$message = clientAdd();
}


#initial values



#test form values and untaint

#HTML with FORM
print $cgi->header();

print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C LogIn", 1, $userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";


print "<form method=\"post\">\n";
#print "  <div class=\"ui-field-contain\">\n";
print "   <label for=\"name\">Name</label>\n";
print "	  <input type=\"textfield\" name=\"name\" id=\"name\">\n";
my $options = {week => "weekly",
	       '2week' => "Every 2 weeks",
	       bimonth => "Bi-monthly",
	       month => "Monthly"};
print selectList({blankoption => 0,
		  multiple => 0,
		  options => $options,
		  name => "schedule",
		  label => "Schedule"
		 });
print "<p>Start Date</p>\n";
print datepicker('startdate', 0, 0 ,0, 1);
print "<p>Applies to Weekly and Every 2 Weeks only</p>";
$options = {7 => "Sunday",
	    1 => "Monday",
	    2 => "Tuesday",
	    3 => "Wednesday",
	    4 => "Thursday",
	    5 => "Friday",
	    6 => "Saturday"};
print selectList({blankoption => 0,
		  multiple => 0,
		  options => $options,
		  name => "dayofweek",
		  label => "Day of Week",
		  sortbykeys => 1
		 });
print "<input type=\"submit\" name=\"submit\" value=\"submit\">\n";
print "</form>\n";
print "</div>";
print $message;
print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";
print $cgi->end_html();

