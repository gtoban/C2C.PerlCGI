#!/usr/bin/perlml
use strict;
use warnings;


use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User :Useredit);
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

my $test;# = $cgi->param('submit');
if ($cgi->param('submit') )
{	
	$updateuser = {
		'userid' => $cgi->param('userid'),
		'firstname' => $cgi->param('firstname'),
		'lastname' => $cgi->param('lastname'),
		'email' => $cgi->param('email'),
		'username' => $cgi->param('username'),
		'rights' => $cgi->param('rights'),
		'clientid' => $cgi->param('clientid'),
	    };
	
	$message = addUpdateUser($updateuser);	
	$edituser = getUserById($cgi->param('userid'));		
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
print "   <label for=\"firstname\">First Name</label>\n";
print "	  <input type=\"textfield\" name=\"firstname\" id=\"firstname\" value=\"$edituser->{'firstname'}\">\n";
print "   <label for=\"lastname\">Last Name</label>\n";
print "	  <input type=\"textfield\" name=\"lastname\" id=\"lastname\" value=\"$edituser->{'lastname'}\">\n";
print "   <label for=\"email\">Email</label>\n";
print "	  <input type=\"textfield\" name=\"email\" id=\"email\" value=\"$edituser->{'email'}\">\n";
print "   <label for=\"username\">Username</label>\n";
print "	  <input type=\"textfield\" name=\"username\" id=\"username\" value=\"$edituser->{'username'}\">\n";

if ($userrights == 3)
{
print "   <label for=\"rights\">Rights</label>\n";
print "	  <select name=\"rights\" id=\"rights\">\n";
print getRights($edituser->{'userrights'});
print "   </select>\n";

print "   <label for=\"clientid\">User Client</label>\n";
print "	  <select name=\"clientid\" id=\"clientid\">\n";
print "    <option value=\"\"></option>\n";
print getClients($edituser->{'userclient'});
print "   </select>\n";
}

print "<input type=\"submit\" name=\"submit\" value=\"submit\">\n";
print "</form>\n";

print "<form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/editpassword.cgi\">";
print "<input type=\"hidden\" name=\"userid\" value=\"$edituser->{'userid'}\">";
print "<input type=\"submit\" name=\"esubmit\" value=\"Edit Password\">";
print "</form>";
print "</div>\n";

print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();

sub getRights
{
	my $right = shift;
	if ($right == 1)
	{
		return "<option value=\"1\">Client</option> <option value=\"2\">Employee</option> <option value=\"3\">Admin</option>";
	}elsif ($right == 2)
	{
		return "<option value=\"1\">Client</option> <option value=\"2\" selected>Employee</option> <option value=\"3\">Admin</option>";	
	}else
	{
		return "<option value=\"1\">Client</option> <option value=\"2\">Employee</option> <option value=\"3\" selected>Admin</option>";
	}
	
	
}

sub getClients {
    	my $clientid = shift;
    	my $clientlist = "";
	my $user = "c2cisAdmin";
	my $pass = "c2cis2015!";

	my $dsn = "DBI:mysql:database=c2cPrograms;host=localhost";
	my $dbh = DBI->connect($dsn,$user,$pass);

	my $drh = DBI->install_driver("mysql");
	
	# Select the data and display to the browser

	my $sth = $dbh->prepare("SELECT * FROM clients");
	$sth->execute();
	while (my $ref = $sth->fetchrow_hashref()) {
	      if ($clientid == $ref->{'id'})
	      {
		$clientlist = $clientlist . "<option value=\"" . $ref->{'id'} . "\" selected>" . $ref->{'name'} . "</option>";
	      }else
	      {
		$clientlist = $clientlist . "<option value=\"" . $ref->{'id'} . "\">" . $ref->{'name'} . "</option>";
	      }
	};

	$sth->finish();
	$dbh->disconnect();
	

	return $clientlist;

}
