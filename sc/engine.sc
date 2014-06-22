s.boot;
s.doWhenBooted({

~reverb_bus = Bus.audio(s, 2);
~sounds = Dictionary[];
~synths = Dictionary[];
~info_subscriber = nil;

~buses = Dictionary[];

OSCresponder.new(nil, "/info_subscribe",
  { arg t, r, msg;
	  var port = msg[1];
	  "info_subscribe to port ".post; port.postln;
	  ~info_subscriber = NetAddr.new("127.0.0.1", port);
	  ~info_subscriber.connect;
  }).add;

OSCresponder.new(nil, "/load",
  { arg t, r, msg;
	  var filename = msg[1].asString;
	  var buf;
	  "loading ".post; filename.postln;
	  buf = Buffer.read(s, filename, 0, -1, {
		  "loaded ".post; filename.postln;
		  "result: ".post; buf.numFrames.postln;
		  if(buf.numFrames > 0, {
			  ~sounds[filename] = buf;
			  if(~info_subscriber != nil, {
				  ~info_subscriber.sendMsg("/loaded", filename, buf.numFrames, buf.sampleRate);
			  });
		  }, {
			  buf.free;
		  });
	  });
  }).add;

OSCresponder.new(nil, "/add_bus",
  { arg t, r, msg;
	  var name = msg[1].asString;
	  "/add_bus ".post; name.postln;
	  ~buses[name] = Bus.audio(s, 2);
	  Synth(\add_reverb_stereo, [
		  \bus, ~buses[name]
	  ]);
  }).add;

SynthDef(\play_stereo, {
	arg buf, out=0, pan=0, fadein=1, amp=1.0, fadeout=1, gate=1, gain=1, looped=0, send=0, sendGain=0;
	var sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf), loop:looped, doneAction:2);
	sig = Balance2.ar(sig[0], sig[1], pan);
	sig = EnvGen.ar(Env.asr(fadein, amp, fadeout, 'linear'), gate, doneAction:2) * sig;
	Out.ar(out, sig * gain);
	Out.ar(send, sig * sendGain);
}).send(s);

SynthDef(\play_mono, {
	arg buf, out=0, pan=0, fadein=1, amp=1.0, fadeout=1, gate=1, gain=1, looped=0, send=0, sendGain=0;
	var sig = PlayBuf.ar(1, buf, BufRateScale.kr(buf), loop:looped, doneAction:2);
	sig = Pan2.ar(sig, pan);
	sig = EnvGen.ar(Env.asr(fadein, amp, fadeout, 'linear'), gate, doneAction:2) * sig;
	Out.ar(out, sig * gain);
	Out.ar(send, sig * sendGain);
}).send(s);

OSCresponder.new(nil, "/play", {
	arg t, r, msg;
    var name = msg[1].asString;
    var pan = msg[2];
    var fade = msg[3];
	var gain_dB = msg[4];
	var looped = msg[5];
	var sendName = msg[6].asString;
    var buf;
    var channel = 0;
	var gain = gain_dB.dbamp;
	var send, sendGain;

	if(sendName == "master", {
		send = 0;
		sendGain = 0;
	}, {
		send = ~buses[sendName];
		sendGain = gain;
	});

    "name:".post; name.postln;
    "pan:".post; pan.postln;
    "fade:".post; fade.postln;
	"gain:".post; gain.postln;
	"sendName:".post; sendName.postln;
    buf = ~sounds[name];
    "buf:".post; buf.postln;
    "send:".post; send.postln;
    "sendGain:".post; sendGain.postln;
    if(buf == nil, {
		"WARNING: sound not found: ".post;
		name.postln;
	}, {
		"numSynths=".post; s.numSynths.postln;
		if(buf.numChannels == 2, {
			~synths[name] = Synth(\play_stereo, [
				\buf, buf,
				\out, channel,
				\pan, pan,
				\fadein, fade,
				\gain, gain,
				\looped, looped,
				\send, send,
				\sendGain, sendGain]);
		}, {
			if(buf.numChannels == 1, {
				~synths[name] = Synth(\play_mono, [
					\buf, buf,
					\out, channel,
					\pan, pan,
					\fadein, fade,
					\gain, gain,
					\looped, looped,
					\send, send,
					\sendGain, sendGain]);
			}, {
				"WARNING: can't play sound with numChannels=".post; buf.numChannels.postln;
			});
		});
	});
}).add; 


SynthDef(\add_reverb_stereo, {
	arg bus, mix = 0.75, room = 0.85, damp = 1.0;
	var signal_l, signal_r, silent_noise, reverb_l, reverb_r;
	silent_noise = WhiteNoise.ar(0.00001); // see http://new-supercollider-mailing-lists-forums-use-these.2681727.n2.nabble.com/cpu-problems-with-PV-MagFreeze-and-Freeverb-tp5998599p6013552.html
	# signal_l, signal_r = In.ar(bus, 2);
	reverb_l = FreeVerb.ar(signal_l + silent_noise, mix, room, damp);
	reverb_r = FreeVerb.ar(signal_r + silent_noise, mix, room, damp);
	Out.ar(0, reverb_l);
	Out.ar(1, reverb_r);
}).send(s);

"langPort=".post; NetAddr.langPort.postln;

});
