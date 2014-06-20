s.boot;
s.doWhenBooted({

~loop_buffers = [
  "water/Sound 2 mindre rinn.wav",
  "water/ZOOM0009a 44100 1.wav",
  "water/ZOOM0009b 44100 1.wav",
  "water/ZOOM0009c 44100 1.wav",
];

~loops = Dictionary[];
~loop_buffers.do(
  { arg item, i;
    var filename = "sound/" ++ item;
    "creating buffer ".post; filename.postln;
    ~loops[item] = Buffer.read(s, filename);
});

~loop_synths = Dictionary[];

SynthDef(\loop, {
	arg buf, out=0, pan=0, fadein=1, amp=1.0, fadeout=1, gate=1, gain=1;
	var sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf), loop:1.0);
	sig = Balance2.ar(sig[0], sig[1], pan) * gain;
	Out.ar(out, EnvGen.ar(Env.asr(fadein, amp, fadeout, 'linear'), gate, doneAction:2) * sig);
}).send(s);

OSCresponder.new(nil, "/loop", {
	arg t, r, msg;
    var name = msg[1].asString;
    var pan = msg[2];
    var fade = msg[3];
	var gain_dB = msg[4];
    var buf;
    var channel = 0;
	var gain = gain_dB.dbamp;
    "received /loop".postln;
    "name:".post; name.postln;
    "pan:".post; pan.postln;
    "fade:".post; fade.postln;
	"gain:".post; gain.postln;
    buf = ~loops[name];
    ~loops[name].postln;
    if(buf == nil) {
    	   "WARNING: sound not found: ".post;
	   name.postln;
	   };
    "numSynths=".post; s.numSynths.postln;
    ~loop_synths[name] = Synth(\loop, [
		\buf, buf,
		\out, channel,
		\pan, pan,
		\fadein, fade,
		\gain, gain]);
}).add; 

"langPort=".post; NetAddr.langPort.postln;

});
