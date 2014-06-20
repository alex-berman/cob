s.boot;
s.doWhenBooted({

~pad_buffers = [
  "water/Sound 2 mindre rinn.wav",
];

~pads = Dictionary[];
~pad_buffers.do(
  { arg item, i;
    var filename = "sound/" ++ item;
    "creating buffer ".post; filename.postln;
    ~pads[item] = Buffer.read(s, filename);
});

~pad_synths = Dictionary[];

SynthDef(\pad_playbuf, {
	arg buf, out=0, pan=0, fadein=1, amp=1.0, fadeout=1, gate=1;
	var sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf), loop:1.0);
	sig = Balance2.ar(sig[0], sig[1], pan);
	Out.ar(out, EnvGen.ar(Env.asr(fadein, amp, fadeout, 'linear'), gate, doneAction:2) * sig);
}).send(s);

OSCresponder.new(nil, "/startPad",
  { arg t, r, msg;
    var name = msg[1].asString;
    var pan = msg[2];
    var fade = msg[3];
    var buf;
    var channel = 0;
    "received /startPad".postln;
    "name:".post; name.postln;
    "pan:".post; pan.postln;
    "fade:".post; fade.postln;
    buf = ~pads[name];
    ~pads[name].postln;
    if(buf == nil) {
    	   "WARNING: sound not found: ".post;
	   name.postln;
	   };
    "numSynths=".post; s.numSynths.postln;
    ~pad_synths[name] = Synth(\pad_playbuf, [
		\buf, buf,
		\out, channel,
		\pan, pan,
		\fadein, fade]);
}).add; 

"langPort=".post; NetAddr.langPort.postln;

});
