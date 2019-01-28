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
use general qw(:addUpdate :get :check);

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
my $itemid;
my $logs;
my $hold;
my $message= "";
if ($cgi->param("edit"))
{
    my $logid = $cgi->param("id");
    my $note = $cgi->param("log");
    if (checkTheseWords($note))
    {
    $hold = addUpdateSimple("UPDATE itemnote SET note = '$note' WHERE id = $logid");
    
    if ($hold->[0])
    {
	$message .= "Note Updated";
    }else
    {
	$message .= "Note NOT Updated: $hold->[1] : $hold->[2]";
    }
    }else
    {
	$message = "Bad Note";
    }
}elsif ($cgi->param("remove"))
{
    my $logid = $cgi->param("id");
    $hold = addUpdateSimple("DELETE FROM itemnote WHERE id = $logid");
    if ($hold->[0])
    {
	$message .= "Note Removed";
    }else
    {
	$message .= "Note NOT Removed. $hold->[1] : $hold->[2]";
    }
    
}
$itemid = $cgi->param("itemid");
$logs = getAnySort(["SELECT * FROM itemnote WHERE itemid = $itemid AND log = 0", 0, 0, 0]);
	    



#test form values and untaint

#HTML with FORM

print $cgi->header();
my $javascript = "<script>\n";
$javascript .= "function confirmDelete() {\n";
$javascript .= "return confirm('Are you sure you want to delete this?');\n";
$javascript .= "}\n";
$javascript .= "</script>\n";
print jqheader($javascript);

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Log Edit", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

print "<form method=\"POST\" action=\"http://www.c2c-hit.net/c2cmobile/task/item.cgi\">\n";
print "<input type=\"hidden\" name=\"itemid\" value=\"$itemid\">\n";
print "<input type=\"submit\" value=\"Back to Item\">\n";
print "</form>\n";
print "<br>";

print "<table data-role=\"table\" id=\"movie-table\" data-mode=\"reflow\" class=\"ui-responsive\">\n";
print " <thead>\n";
print " <tr>\n";
print "  <th data-priority=\"2\">Note</th>\n";
print "  <th data-priority=\"3\">Action</th>\n";
print " </tr>\n";
print " </thead>\n";
print "<tbody>\n";
foreach my $log (@{$logs->[0]})
{
    print "<tr>\n";
    
    print "<td>";
    print "<form method=\"POST\">\n";
    print "<input type=\"hidden\" name=\"itemid\" value=\"$itemid\">\n";
    print "<input type=\"hidden\" name=\"id\" value=\"$log->{'id'}\">\n";
    print textArea({name => 'log', lable => 'log', value => $log->{'note'}, hidelabel => "1"});
    print "<input type=\"submit\" name=\"edit\" value=\"Edit\">\n";
    print "</form>\n";
    print "</td>\n";
    print "<td>";
    print "<form method=\"POST\" onsubmit=\"return confirmDelete()\">\n";
    print "<input type=\"hidden\" name=\"itemid\" value=\"$itemid\">\n";
    print "<input type=\"hidden\" name=\"id\" value=\"$log->{'id'}\">\n";
    print "<input type=\"submit\" name=\"remove\" value=\"Remove\">\n";
    print "</form>\n";
    print "</td>\n";
    #print "<td></td><td></td>\n";
    print "</tr>\n";
}
print "</tbody></table>\n";

print "</div>\n";

if ($message)
{
    print "<script> alert(\"$message\")</script>";
}



print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


