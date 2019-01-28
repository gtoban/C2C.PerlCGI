#!/usr/bin/perlml
use strict;
use warnings;


use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User :Useredit :Usercheck);
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
my $edituser;
my $message;
my $updateuser;
my $updatepass;
my $updateid;

my $test;# = $cgi->param('submit');
if ($cgi->param('submit') )
{
    $edituser = getUserById($cgi->param('userid'));
    if ($userid == $edituser->{'userid'})
    {
	
	if (login($edituser->{'username'}, $cgi->param('currentpass')))
	{
		if ($cgi->param('newpass') eq $cgi->param('verifypass'))
		{
			$updatepass = $cgi->param('newpass');
			$updateid = $cgi->param('userid');
			$message = updatePassword($updateid, $updatepass);
		}else
		{
			$message = "Your new password and verify password do not match";
		}
	}else
	{
		$message = "Your current password is not correct.";
	}
    }else
    {
	if ($cgi->param('newpass') eq $cgi->param('verifypass'))
	{
		$updatepass = $cgi->param('newpass');
		$updateid = $cgi->param('userid');
		$message = updatePassword($updateid, $updatepass);
	}else
	{
		$message = "Your new password and verify password do not match";
	}
    }
	
		
			
}elsif ($cgi->param('esubmit'))
{
	$edituser = getUserById($cgi->param('userid'));
}else
{
	$edituser = getUserById($userid);
}




#test form values and untaint

#HTML with FORM
print $cgi->header();

print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C LogIn", 1, $userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
print $message;
print "<form method=\"post\">\n";
print "<input type=\"hidden\" name=\"userid\" value=\"$edituser->{'userid'}\">\n";
#print "  <div class=\"ui-field-contain\">\n";
if ($userid == $edituser->{'userid'})
{
	print "   <label for=\"currentpass\">Current Password</label>\n";
	print "	  <input type=\"password\" name=\"currentpass\" id=\"currentpass\">\n";
}
print "   <label for=\"newpass\">New Password</label>\n";
print "	  <input type=\"password\" name=\"newpass\" id=\"newpass\">\n";
print "   <label for=\"verifypass\">Verify Password</label>\n";
print "	  <input type=\"password\" name=\"verifypass\" id=\"verifypass\">\n";
print "<input type=\"hidden\" name=\"userid\" value=\"$edituser->{'userid'}\">";
print "<input type=\"submit\" name=\"submit\" value=\"submit\">\n";
print "</form>\n";
print "</div>\n";

print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


