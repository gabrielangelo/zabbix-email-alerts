#!/usr/bin/perl

# Envio de gráfico por email através do ZABBIX (Send zabbix alerts graph mail)
#
# 
# Copyright (C) <2016>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contacts:
# Eracydes Carvalho (Sansão Simonton) - NOC Analyst - sansaoipb@gmail.com
# Thiago Paz - NOC Analyst - thiagopaz1986@gmail.com

use strict;
use warnings;
use MIME::Lite;
use HTTP::Cookies;
use WWW::Mechanize; 
use JSON::RPC::Client;
use Data::Dumper;
use Encode;
use POSIX;

## Dados do Zabbix ##############################################################################################################
my $server_ip  = 'http://127.0.0.1/zabbix'; # URL de acesso ao FRONT com "http://"
my $user       = 'Admin';
my $password   = 'zabbix';
my $client     = new JSON::RPC::Client;
my ($json, $response, $authID);
#################################################################################################################################

## Configuracao do Grafico ######################################################################################################
my $width   = 600;  # Largura
my $height  = 100;  # Altura
my $stime   = strftime("%Y%m%d%H%M%S", localtime( time-3600 )); # Hora inicial do grafico [time-3600 = 1 hora atras]
#################################################################################################################################

## Separando argumentos #########################################################################################################
my ($itemname, $eventid, $itemid, $color, $period, $body) = split /\#/, $ARGV[2], 6;
#################################################################################################################################
$eventid =~ s/^\s+//;
#################################################################################################################################
unless ($itemid){
                print "<<< Item inválido ou USER do front sem permissão de leitura no host >>>\n";
                exit;
}

my $graph = "/tmp/$itemid.png";

my $mech = WWW::Mechanize->new();
$mech->cookie_jar(HTTP::Cookies->new());
$mech->get("$server_ip/index.php?login=1");
$mech->field(name => $user);
$mech->field(password => $password);
$mech->click();

my $png = $mech->get("$server_ip/chart3.php?name=$itemname&period=$period&width=$width&height=$height&stime=$stime&items[0][itemid]=$itemid&items[0][drawtype]=5&items[0][color]=$color");

open my $image, '>', $graph or die $!;
$image->print($png->decoded_content);
$image->close;
#################################################################################################################################

## Bom dia, boa tarde ou boa noite ##############################################################################################
my $hour = strftime '%H', localtime;
my $salutation;
if ($hour < "12")
{
	$salutation = "Bom dia"; #Good Morning
}
elsif ($hour >= "18")
{
	$salutation = "Boa noite"; #Good Night
}
else
{
	$salutation = "Boa tarde"; #Good Afternoon
}
#################################################################################################################################

utf8::decode($ARGV[1]);
utf8::decode($ARGV[2]);

my $historico = &get_history;

if ((&tipo == 0) || (&tipo == 3)) {

	my $msg = MIME::Lite->new(
					From    => 'ZABBIX <noc@monitoramento.com>',
					To      => $ARGV[0],
					Subject => encode('MIME-Header',$ARGV[1]),
					Type    => 'multipart/related'
	);
	$msg->attach(
			Type => 'text/html',
			Data => qq{<meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
			<body>
			<p>$salutation,</p>
			<p>$body</p>
			<p><img src="cid:grafico.png"></p>
			<p>$historico</p>
			</body>}
	);
	$msg->attach(
			Type => 'AUTO',
			Id   => 'grafico.png',
			Path => $graph,
	);
	$msg->send();
			if ($msg->last_send_successful) {
			&ack; 
			&logout;
			}
}
else {
	my $msg = MIME::Lite->new(
					From    => 'ZABBIX <noc@monitoramento.com>',
					To      => $ARGV[0],
					Subject => encode('MIME-Header',$ARGV[1]),
					Type    => 'multipart/related'
);
	$msg->attach(
			Type => 'text/html',
			Data => qq{<meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
			<body>
			<p>$salutation,</p>
			<p>$body</p>
			<p>$historico</p>
			</body>}
	);
	$msg->send();
			if ($msg->last_send_successful) {
			&ack; 
			&logout;
			}
}

unlink ("$graph");

sub tipo {
	$json = {
		jsonrpc => '2.0',
		method  => 'user.login',
		params  => {
			user  => $user  ,
			password => $password
     		},
   		id => 1
  	};

	$response = $client->call("$server_ip/api_jsonrpc.php", $json);
	#print Dumper ($response);
	unless ($response){
    print "<<< URL declarada para o front errada >>>\n";
    exit;
    }
        unless ($response->content->{'result'}){
        print "<<< Usuário ou senha inválido >>>\n";
        exit;
        }	
		
	$authID = $response->content->{'result'};
	$itemid =~ s/^\s+//;

	$json = {
		jsonrpc => '2.0',
	   	method  => 'item.get',
		params  => {
			output => ['value_type'],
			itemids => $itemid,
                        webitems => $itemid
     		},
   		auth => $authID,
		id => 2
  	};
	$response = $client->call("$server_ip/api_jsonrpc.php", $json);
	#print Dumper ($response);
	
        my $itemtype;
        foreach my $get_itemtype (@{$response->content->{result}}) {
                $itemtype = $get_itemtype->{value_type}
        }
        unless (defined $itemtype){
                print "<<< Item inválido ou USER do front sem permissão de leitura no host >>>\n";
                exit;
        }

        return $itemtype;
}

sub ack {
	$json = {
		jsonrpc => '2.0',
		method  => 'event.acknowledge',
		params  => {
			eventids  => $eventid,
			message => "Email enviado com sucesso para $ARGV[0]"
		},
		auth => $authID,
		id => 3
	};

	$response = $client->call("$server_ip/api_jsonrpc.php", $json);
	#print Dumper ($response);
}

sub logout {
	$json = {
   		jsonrpc => '2.0',
		method => 'user.logout',
		params => [],
		id => 4,
		auth => $authID
  	};
	$client->call("$server_ip/api_jsonrpc.php", $json);
}

sub get_history {
	$json = {
		jsonrpc => '2.0',
                method  => 'history.get',
                params  => {
			output => "extend",
        		history => 1,
        		itemids =>  $itemid,
        		sortfield => "clock",
        		sortorder => "DESC",
                },
                auth => $authID,
                id => 3
        };
	
	$response = $client->call("$server_ip/api_jsonrpc.php", $json);
	my $last_item  = $response->content->{result}[-1];
	return $last_item;	
}
	
exit;

