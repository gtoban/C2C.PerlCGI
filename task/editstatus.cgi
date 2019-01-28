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
use general qw(:get :check);
use itemDatabase qw(:Itemstatus);

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
my $allstatuses;
my $statusestoedit;
my $hold;
my $temp;
my $newstatus;
my $message = "";


#test form values and untaint

if ($cgi->param("submit"))
{    
    $allstatuses = getAnySort(["SELECT * FROM itemstatus", 0, 0, 0]);
    foreach my $item (@{$allstatuses->[0]})
    {
	if ($item->{'id'} != 1 && $item->{'id'} != 2)
	{
	    $temp = $cgi->param("$item->{'id'}:status");
	    if (checkTheseWords($temp))
	    {
		$hold = addEditItemStatus($item->{'id'}, $temp);
		
	    }else
	    {
		$message .= "Bad Status. ";
	    }
	}
    }
}elsif ($cgi->param("addnew"))    
{
    $newstatus = $cgi->param("newstatus");
    if (checkTheseWords($newstatus))
    {
    	$hold = addEditItemStatus(0,$newstatus);
    }else
    {
    	$message .= "Bad Status";
    }
    
}


$allstatuses = getAnySort(["SELECT * FROM itemstatus"]);


#HTML with FORM

print $cgi->header();
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Edit Statuses", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
print "<p>$message</p>\n";
print "<form method=\"POST\">\n";
print textInput({'name' => "newstatus", 'label' => "Status", 'value' => ""});
print "<input type=\"submit\" name=\"addnew\" value=\"Add New\">\n";

print "</form>\n";

print "<form method=\"POST\">\n";

foreach my $status (@{$allstatuses->[0]})
{
    if ($status->{'id'} == 1 || $status->{'id'} == 2)
    {
	print textInput({'name' => "", 'label' => "Status", 'value' => $status->{'name'}, 'readonly' => 1});
    }else
    {
	print textInput({'name' => "$status->{'id'}:status", 'label' => "Status", 'value' => $status->{'name'}});
    }
}

print "<input type=\"submit\" name=\"submit\" value=\"Update\">\n";

print "</form>\n";




#
#CONTENT MAIN END
#
print "</div>\n";




print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


