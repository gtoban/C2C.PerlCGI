#!/usr/bin/perlml
use strict;
use warnings;

use DBI;
use CGI::Session;
use CGI;
use Mail::Sendmail;
use lib '/home/c2cmedical/public_html/c2c/modules';
#use Manager qw(:User :Usercheck :Useredit);
use htmlManager qw(:elements);
use clientManager qw(:Client);
use timeManager qw(:Parts);




my $updateuser = {
                'timeid' => "4",
		'userid' => "2",
		'clientid' => "2",
		'datetype' => "Day",
		'timedate' => "2015-09-09",
		'hours' => "20",
		'description' => "lkjlkj",
		'status' => "1",
	    };
my $val = addUpdateTime($updateuser);
print $val->[0];
#print updatePassword(2, "culleoka87"). "\n";

my %mail = ( To      => 'c2c_is@c2c-hit.net',
            From    => 'gtoban87@gmail.com',
            Message => "This is a very short message"
           );

#print sendmail(%mail);# or die $Mail::Sendmail::error;

#print getClients();
#print getUserByEmail("gabriel.toban\@c2c-hit.net");
#my %criteria = ('user' => ['2'],
#                'fromdate' => "2015-10-09");
#my $sort = [['1','user', 'ASC'],['2', 'client', 'DESC']];

#my $ref = getTimes();#(\%criteria, $sort);

#print "$ref->[0] || $ref->[1] || $ref->[2]";

	
