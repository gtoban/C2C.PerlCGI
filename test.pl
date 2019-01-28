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
use itemDatabase qw(:Itemstatus :Itemuserquery :Itemtag :Item :Itemgroups);
use general qw(:get :addUpdate :check);
use email qw(:item);




#my $updateitem = [18,2, {
#		'clientid' => "2",
#		'name' => "Day",
#		'description' => "HELP",
#		'statusid' => "2",
#	    }];
#my $val = addUpdateTime($updateuser);
#print $val->[0];
#print updatePassword(2, "culleoka87"). "\n";

#my %mail = ( To      => 'c2c_is@c2c-hit.net',
#            From    => 'gtoban87@gmail.com',
#            Message => "This is a very short message"
#           );
#
#print sendmail(%mail);# or die $Mail::Sendmail::error;

#print getClients();
#print getUserByEmail("gabriel.toban\@c2c-hit.net");
#my %criteria = ('user' => ['2'],
#                'fromdate' => "2015-10-09");
#my $sort = [['1','user', 'ASC'],['2', 'client', 'DESC']];

#my $ref = getTimes();#(\%criteria, $sort);

#print "$ref->[0] || $ref->[1] || $ref->[2]";

#my $hold = getAnySort(["SELECT id from users", 0, 0 ,0]);
#my $prefs = getAnySort(["SELECT id from itempreferences", 0, 0, 0]);
#my $query = "INSERT INTO itemuserpreferences (userid, preferenceid)VALUES ";
#my $first = 1;
#
#foreach my $user (@{$hold->[0]})
#{
#    foreach my $pref (@{$prefs->[0]})
#    {
#	if ($first)
#	{
#	    $query .= "($user->{'id'}, $pref->{'id'})";
#	    $first = 0;
#	}else
#	{
#	    $query .= ", ($user->{'id'}, $pref->{'id'})";
#	}
#    }
#}
#my $temp = addUpdateSimple($query);
#print $temp->[0];

#itemEmail(['Gabriel', 'name','desc', 'changed', 'gabriel.toban@c2c-hit.net']);
#print addItemGroups();

#my $hold = getAnySort(["SELECT * FROM users", 0, 0, 0]);
#my $hold1;
#my $message = "";
#foreach my $user (@{$hold->[0]})
#{
#    $hold1 = itemUserQuery($user->{'id'}, $user->{'rights'});
#    $message = "$hold1->[0] :: $hold1->[1]\n";
#}
#print $message;
my $hold = addEditItemStatus(5,"TEST");
print $hold->[2];

	
