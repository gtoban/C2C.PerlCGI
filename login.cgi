#!/usr/bin/perlml
use strict;
use warnings;

use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User :Usercheck);
use htmlManager qw(:elements);

my $cgi = CGI->new;
my $session;
my $cookie = "";


my $err = "";
my $nologin = 1;
if ($cgi->param('submit'))
{
	if (Check($cgi->param('username'), $cgi->param('password')))
	{
		#my $url = "?sid=$sid";
		my %user = login($cgi->param('username'), $cgi->param('password'));
		if ($user{"userid"})
		{
			$session = new CGI::Session(undef, undef, {Directory=>'/tmp'});
			$cookie = $cgi->cookie(CGISESSID => $session->id);
			$session->expire(300);
			
			$session->param("userid",$user{"userid"});
			$session->param("userfirstname",$user{"firstname"});
			$session->param("userlastname",$user{"lastname"});
			$session->param("useremail",$user{"email"});
			$session->param("username",$user{"username"});
			$session->param("userrights",$user{"userrights"});
			$session->param("userclientid",$user{"userclientid"});
			$nologin = 0;
			#print $cgi->redirect(-url=>'http://www.c2c-hit.net/c2cmobile/home.cgi');
		}else
		{
			$err = "Login Failed";
		}
	
		
	}else
	{
		$err = "Login Failed";
	}	
}else
{
	$session = new CGI::Session(undef, $cgi, {Directory=>'/tmp'});
	$session->flush();
	$session->clear();
	$session->delete();
	$cookie = $cgi->cookie(CGISESSID => $session->id);
	$cookie->expires(1);

}

#initial values



#HTML with FORM

print $cgi->header( -cookie=>$cookie );
#-cookie=>$cookie );

#print $cgi->start_html("C2C Log in"), $cgi->h1("Welcome to C2C IS Login");
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C LogIn");
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

if ($nologin)
{

print " <p>Please provide username and password.</p> <br><br>\n";
print " <form method=\"post\">\n";
print "  <div class=\"ui-field-contain\">\n";
print "   <label for=\"username\">Username</label>\n";
print "   <input type=\"text\" name=\"username\" id=\"username\">\n";
print "   <label for=\"password\">Password</label>\n";
print "   <input type=\"password\" name=\"password\" id=\"password\">\n";
print "  </div>\n";
print "  <input type=\"submit\" data-inline=\"true\" name=\"submit\" value=\"Submit\">\n";
print " </form>\n";
print "<p>Forgot your password? <a href=\"http://www.c2c-hit.net/c2cmobile/forgotpassword.cgi\">Click Here</a></p>";
print "<p>$err</p>";
}else
{
print "<p>You have successfully logged in. <form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/home.cgi\"><input type=\"submit\" value=\"Click Here\"></form> to continue.</p>\n";
}

print "</div>\n";


print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";


print $cgi->end_html;


sub Check
{
	my $uname = $_[0];
	my $pword = $_[1];

	if (!checkUsername($uname))
	{
		return 0;
	}
	if (!checkPassword($pword))
	{
		return 0;
	}


	return 1;

}


