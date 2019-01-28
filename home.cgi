#!/usr/bin/perl
use cPanelUserConfig;
use strict;
use warnings;


use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User :Usercheck);
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



#test form values and untaint

#HTML with FORM

print $cgi->header();
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Home", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
print "<p> $userclientid </p>\n";

print "<h1>Time Sheet</h1>\n";
print "<table data-role=\"table\" class=\"ui-responsive\">\n";
print "      <thead>\n";
print "        <tr>\n";
if ($userrights > 1)
{
print "         <th>Enter Time</th>\n";
}
print "         <th>Time Search</th>\n";
if ($userrights == 3)
{
print "         <th>Time Collect</th>\n";
}
print "        </tr>\n";
print "      </thead>\n";

print "      <tbody>\n";
if ($userrights > 1)
{
print "        <tr>\n";
print "          <td>\n";
print "              <form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/time/entertime.cgi\">\n               <input type=\"submit\" name=\"esubmit\" value=\"Click Here\">\n              </form>";
print "          </td> ";
}
print "          <td>\n";
print "              <form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/time/timesearch.cgi\">\n               <input type=\"submit\" name=\"esubmit\" value=\"Click Here\">\n              </form>";
print "          </td> ";
if ($userrights == 3)
{
print "          <td>\n";
print "              <form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/time/collect/collect.cgi\" target=\"_blank\">\n               <input type=\"submit\" name=\"esubmit\" value=\"Click Here\">\n              </form>";
print "          </td> ";
}
print "        </tr>";	
print "      </tbody>\n";
print "</table>\n";

print "</div>";


print "<h1> Tasks and Tickets </h1>\n";
print "<a href=\"http://www.c2c-hit.net/c2cmobile/task/taskhome.cgi\" target=\"_blank\"class=\"ui-btn ui-corner-all\">Go To Task Home</a>\n";

print "<h1> Compliance </h1>\n";
print "<a href=\"http://www.c2c-hit.net/c2cmobile/compliance/geninfo2016.cgi\" target=\"_blank\"class=\"ui-btn ui-corner-all\">Meaningful Use: General Information</a>\n";

print "</div>\n";




print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


