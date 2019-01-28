#!/usr/bin/perlml
use strict;
use warnings;


use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
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
my @userlist;
my $right;


#test form values and untaint

#HTML with FORM
print $cgi->header();
 
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C LogIn", 1, $userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

print "<a href=\"http://www.c2c-hit.net/c2cmobile/newuser.cgi\">Create New User</a>";
@userlist = getUsers();

print "<table data-role=\"table\" class=\"ui-responsive\">\n";
print "      <thead>\n";
print "        <tr>\n";
print "         <th>First Name</th>\n";
print "          <th>Last Name</th>\n";
print "          <th>Email</th>\n";
print "          <th>Username</th>\n";
print "          <th>User Rights</th>\n";
print "          <th>User Client</th>\n";
print "          <th>Edit</th>\n";
print "        </tr>\n";
print "      </thead>\n";
print "      <tbody>\n";
foreach my $user (@userlist)
{

	if ($user->{'userrights'} == 1)
	{
		$right = "Client";
	}elsif ($user->{'userrights'} == 2)
	{
		$right = "Employee";
	}else
	{
		$right = "Admin";
	}

print "        <tr>\n";
print "          <td>$user->{'firstname'}</td>\n";
print "          <td>$user->{'lastname'}</td>\n";
print "          <td>$user->{'email'}</td>\n";
print "          <td>$user->{'username'}</td>\n";
print "          <td>$right</td>\n";
print "          <td>$user->{'userclient'}</td>\n";
print "          <td>\n";
print "              <form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/edituser.cgi\">\n               <input type=\"hidden\" name=\"userid\" value=\"$user->{'userid'}\">\n               <input type=\"submit\" name=\"esubmit\" value=\"Edit\">\n              </form>";
print "          </td> ";
print "        </tr>";	
}
print "      </tbody>\n";
print "</table>\n";
print "</div>\n";

print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


