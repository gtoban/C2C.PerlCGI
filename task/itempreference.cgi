#!/usr/bin/perlml
use strict;
use warnings;


use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User :Usercheck);
use htmlManager qw(:elements);
use general qw(:get :addUpdate);

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
my $prefs;
my $myprefs;
my $checkbox;
my $message = "";

#test form values and untaint

if ($cgi->param('submit'))
{
	my $query;
	my $qresult;
	my $temailfor = "\nEmail me for updates on: ";
	my $tnoemail = "\nDo not email me for updates on: ";
	my $emailfor = "";
	my $noemail = "";
	$prefs = getAnySort(["SELECT * FROM itempreferences WHERE userright <= $userrights",0 ,0 ,0]);
	foreach my $pref (@{$prefs->[0]})
	{
		$query = "UPDATE itemuserpreferences SET ";
		if ($cgi->param($pref->{'name'}))
		{
			$query .= "preference = 1 ";
			$query .= "WHERE preferenceid = $pref->{'id'} and userid = $userid";
			$emailfor = " $pref->{'name'}";
		}else
		{
			$query .= "preference = 0 ";
			$query .= "WHERE preferenceid = $pref->{'id'} and userid = $userid";
			$noemail = " $pref->{'name'}";
		}
		$qresult = addUpdateSimple($query);
		if ($qresult->[0])
		{
			$temailfor .= " $emailfor ";
			$tnoemail .=  " $noemail ";
		}else
		{
			$message .= "Error: $qresult->[1] : $qresult->[2]";
		}
		#$message = "QUERY: $query";
	}
	$message .= "$temailfor $tnoemail";
}

#HTML with FORM

print $cgi->header();
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Item Preferences", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
$prefs = getAnySort(["SELECT * FROM itempreferences WHERE userright <= $userrights",0 ,0 ,0]);
$myprefs = getAnySort(["SELECT * FROM itemuserpreferences WHERE userid = $userid",0 ,0 ,0]);
my $count = 0;
foreach my $pref (@{$prefs->[0]})
{	
	foreach my $mypref (@{$myprefs->[0]})
	{
		if ($mypref->{'preferenceid'} == $pref->{'id'})
		{
			$checkbox->[$count] = [$pref->{'name'}, $pref->{'name'}, $pref->{'id'}, $mypref->{'preference'}]; 
			$count += 1;
			last;
		}
	}
}

print "<h1>Item Preferences</h1>\n";
print "<p>Check the boxes that you want to be notified of when they change on an item that you are associated with or that you have created.</p>";
print "<form method=\"POST\">\n";

print checkbox($checkbox);
print "<input type=\"submit\" name=\"submit\" value=\"Submit\">\n";
print "</form>\n";



print "</div>\n";

if ($message)
{
	print "<script> alert(\"$message\")</script>";
}



print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";


print $cgi->end_html();


