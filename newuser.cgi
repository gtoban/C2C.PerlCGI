#!/usr/bin/perlml
use strict;
use warnings;

use Crypt::PBKDF2;
use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User :Usercheck :Useredit);
use htmlManager qw(:elements);

my $pbkdf2 = Crypt::PBKDF2->new(
	hash_class => 'HMACSHA2',
	hash_args => {
		sha_size => 512,
	},
    iterations => 10000,
    salt_len => 10,
);

my $cgi = CGI->new;
my $sid = $cgi->cookie('CGISESSID') || $cgi->param('CGISESSID') || undef;
my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});

#my $userid = $session->param("userid");
my $userrights = 0;
if ($session->param("userid"))
{
	my $userid = $session->param("userid");
	my $userfirstname = $session->param("userfirstname");
	my $userlastname = $session->param("userlastname");
	my $useremail = $session->param("useremail");
	my $userclientid = $session->param("userclientid");
	$userrights = $session->param("userrights");
}else
{
	print $cgi->redirect(-url=>'http://www.c2c-hit.net/c2cmobile/login.cgi');			
}

my $updateuser;
my $message = "";
if ($cgi->param('submit'))
{
	$updateuser = {
		'firstname' => $cgi->param('firstname'),
		'lastname' => $cgi->param('lastname'),
		'email' => $cgi->param('email'),
		'username' => $cgi->param('username'),
		'password' => $cgi->param('username'),
		'rights' => $cgi->param('rights'),
		'clientid' => $cgi->param('clientid'),
	    };
	$message = addUpdateUser($updateuser);
	#$message = userAdd();
}


#initial values



#test form values and untaint

#HTML with FORM
print $cgi->header();

print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C LogIn", 1, $userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";


print "<form method=\"post\">\n";
#print "  <div class=\"ui-field-contain\">\n";
print "   <label for=\"firstname\">First Name</label>\n";
print "	  <input type=\"textfield\" name=\"firstname\" id=\"firstname\">\n";
print "   <label for=\"lastname\">Last Name</label>\n";
print "	  <input type=\"textfield\" name=\"lastname\" id=\"lastname\">\n";
print "   <label for=\"email\">Email</label>\n";
print "	  <input type=\"textfield\" name=\"email\" id=\"email\">\n";
print "   <label for=\"username\">Username</label>\n";
print "	  <input type=\"textfield\" name=\"username\" id=\"username\">\n";
print "   <label for=\"password\">Password</label>\n";
print "	  <input type=\"textfield\" name=\"password\" id=\"password\">\n";
print "   <label for=\"rights\">Rights</label>\n";
print "	  <select name=\"rights\" id=\"rights\">\n";
print "	    <option value=\"1\">Client</option>\n";
print "	    <option value=\"2\">Employee</option>\n";
print "	    <option value=\"3\">Admin</option>\n";
print  "  </select>\n";
print "   <label for=\"clientid\">User Client</label>\n";
print "	  <select name=\"clientid\" id=\"clientid\">\n";
print "	    <option value=\"\"></option>\n";
print getClients();
print "   </select>\n";
#print " </div>\n";
print "<input type=\"submit\" name=\"submit\" value=\"submit\">\n";
print "</form>\n";
print "</div>";
#print $message;
if ($message)
{
	print "<script> alert(\"$message\")</script>";
}
print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";
print $cgi->end_html();

#-----------------------
#----------------------
#------------------------Subroutines
#---------------------
#---------------------

sub getClients {

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
	      $clientlist = $clientlist . "<option value=\"" . $ref->{'id'} . "\">" . $ref->{'name'} . "</option>";
	};

	$sth->finish();
	$dbh->disconnect();
	

	return $clientlist;

}

sub userAdd
{
	my $columns = "(";
	my $values = "(";
	my $query = "INSERT INTO users ";
	
	if (checkName($cgi->param('firstname')))
	{		
		$columns = $columns . "firstName, ";
		$values = $values . "'" . $cgi->param('firstname') . "', ";
	}else
	{
		return "Firstname must be letters only.";
	}
	if (checkName($cgi->param('lastname')))
	{
		$columns = $columns . "lastName, ";
		$values = $values . "'" . $cgi->param('lastname') . "', ";
	}else
	{
		return "Lastname must be letters only.";
	}
	if (checkEmail($cgi->param('email')))
	{
		$columns = $columns . "email, ";
		$values = $values . "'" . $cgi->param('email') . "', ";
	}else
	{
		return "Email is not valid.";
	}
	if (checkUsername($cgi->param('username')))
	{
		if (getUserByUsername($cgi->param('username')))
		{
			return "Username already exist.";
		}
		$columns = $columns . "username, ";
		$values = $values . "'" . $cgi->param('username') . "', ";
	}
	else
	{
		return "Username is not valid.";
	}
	if (checkPassword($cgi->param('password')))
	{
		$columns = $columns . "password, ";
		$values = $values . "'" . $pbkdf2->generate($cgi->param('password')) . "', ";
	}
	else
	{
		return "Password is not valid.";
	}
	if ($cgi->param('rights'))
	{
		$columns = $columns . "rights ";
		$values = $values . $cgi->param('rights');
		if ($cgi->param('rights') == 1)
		{
			$columns = $columns . ", ";
			$values = $values . ", ";
			if ($cgi->param('clientid'))
			{
					$columns = $columns . "clientId ";
					$values = $values . $cgi->param('clientid');
			}
			else
			{
				return "If client rights are given then a client must be identified";
			}
		}
	}
	$columns = $columns . ") ";
	$values = $values . ")";
	$query = $query . $columns . "VALUES " . $values;
	#return $query;
	return addUser($query);
}



