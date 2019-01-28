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


#initial values
my $edituser;
my $message;
my $updateuser;
my $updatepass;
my $updateid;

my $test;# = $cgi->param('submit');
if ($cgi->param('uid') )
{
    $edituser = getUserById($cgi->param('uid'));
}
    		
if ($cgi->param('submit'))
{
	$edituser = getUserById($cgi->param('userid'));
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




#test form values and untaint

#HTML with FORM
print $cgi->header();

print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C LogIn");
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
print $message;
print "<form method=\"post\">\n";
#print "  <div class=\"ui-field-contain\">\n";
print "   <label for=\"newpass\">New Password</label>\n";
print "	  <input type=\"password\" name=\"newpass\" id=\"newpass\">\n";
print "   <label for=\"verifypass\">Verify Password</label>\n";
print "	  <input type=\"password\" name=\"verifypass\" id=\"verifypass\">\n";
print "<input type=\"hidden\" name=\"userid\" value=\"$edituser->{'userid'}\">";
print "<input type=\"submit\" name=\"submit\" value=\"submit\">\n";
print "</form>\n";
print "<p>To login <form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/login.cgi\">\n  <input type=\"submit\" value=\"Click Here\">\n  </form> </p>\n";
print "</div>\n";

print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


