#!/usr/bin/perlml
use strict;
use warnings;

use Data::Dumper;
use Date::Calc qw(Today Now);
use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use timeManager qw(:Parts);
use clientManager qw(:Client);
use Manager qw(:User :Usercheck);
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

#print $cgi->redirect(-url=>"http://www.c2c-hit.net/c2cmobile/time/collect/gt.txt");

my %criteria = (
   'status' => [1]);

my $sort = [[1, 'client', 'DESC'], [2, 'user', 'DESC']];

my $ref = getTimes(\%criteria, $sort);
my $times = $ref->[0];

my ($hour,$min,$sec) = Now();
my ($year,$month,$day) = Today();

my $filename = "$userid$year$month$day$hour$min$sec" . ".txt";

#print Data::Dumper->Dump(@{$times});

open (my $fh, ">$filename") or die "Could not open file";
my $retval;
my $client;
my $clientid;
my $user;
my $output = "";
foreach my $time (@{$times})
{
	#print $time;
	#print Data::Dumper->Dump($time);
	$clientid = $time->{'clientid'};
	$client = getClientById($clientid);
	$user = getUserById($time->{'userid'});
	$output = $client->{'name'};
	$output .= ";";
	$output .= "$user->{'firstname'} $user->{'lastname'}";
	$output .= ";";
	$output .= "$time->{'hours'}\n";
	print $fh "$output";
	
	$time->{'status'} = 2;
	#$retval = addUpdateTime($time);
}


close $fh;

#$filename = "gt.txt";
print $cgi->redirect(-url=>"http://www.c2c-hit.net/c2cmobile/time/collect/$filename");			


