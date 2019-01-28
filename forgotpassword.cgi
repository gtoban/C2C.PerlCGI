#!/usr/bin/perlml
use strict;
use warnings;


use DBI;
use CGI::Session;
use CGI;
use Mail::Sendmail;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User);
use htmlManager qw(:elements);

my $cgi = CGI->new;


#initial values
my $edituser;
my $uid;
my $email;
my $link;
my %mail;
my $message;
my $success = 0;

my $test;# = $cgi->param('submit');
if ($cgi->param('submit') )
{
    $email = $cgi->param('email');
    $edituser = getUserByEmail($email);
    if ($edituser)
    {
	$uid = $edituser->{'userid'};
	$link = "http://www.c2c-hit.net/c2cmobile/forgotpasswordupdate.cgi?uid=$uid";
	%mail = ( To      => $email,
	From    => 'gtobanit@gmail.com',
	Message => "Click this link to change your password:\n$link",
	);
	$success = sendmail(%mail);
	if ($success)
	{
		$message = "Please check your email. Email sent successfully.";
	}else
	{
		$message = "Email not successful.";
	}
    }else
    {
	$message = "That email is not associated with a user.";
    }
}




#test form values and untaint

#HTML with FORM
print $cgi->header();

print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Forgot Password");
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
print $message;
if (!$success)
{
print "<p>Please enter the email associated with your account.</p>";
print "<form method=\"post\">\n";
print "   <label for=\"email\">email</label>\n";
print "	  <input type=\"textfield\" name=\"email\" id=\"email\">\n";
print "<input type=\"submit\" name=\"submit\" value=\"submit\">\n";
print "</form>\n";
}
print "<p>If you have any additional problems please contact Coast to Coast at 865-209-6586.</p>";
print "</div>\n";




print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";


print $cgi->end_html();


