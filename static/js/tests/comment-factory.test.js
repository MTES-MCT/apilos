const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

test("comment factories share one dialog and reset drafts on opening and successful submission", async () => {
  const elements = new Map();
  const dialogs = [];
  function element(tagName) {
    return {
      tagName,
      classList: { add() {}, remove() {}, contains() { return false; } },
      style: {},
      setAttribute(name, value) {
        if (name === "id") this.id = value;
        this[name] = value;
      },
      appendChild(child) {
        child.parentNode = this;
        if (child.id) elements.set(child.id, child);
      },
      addEventListener() {},
      set innerHTML(value) {
        if (tagName === "dialog") {
          elements.set("textarea_main_comment_modal", element("textarea"));
          elements.set("loading", element("div"));
          elements.set("main_comment_modal-title_text", element("span"));
          elements.set("main_comment_modal_comments", element("div"));
          elements.set("main_comment_modal-submit", element("button"));
        }
      },
    };
  }
  const document = {
    createElement: element,
    getElementById: (id) => elements.get(id) || null,
    getElementsByName: () => [{ value: "csrf" }],
    body: {
      append(dialog) {
        dialogs.push(dialog);
        elements.set(dialog.id, dialog);
      },
    },
  };
  const first = element("div");
  const second = element("div");
  const refresh = element("button");
  let refreshes = 0;
  refresh.click = () => { refreshes++; };
  elements.set("first", first);
  elements.set("second", second);
  elements.set("refresh_opened_comments", refresh);
  let success = true;
  const requests = [];
  const fetch = async (url, options) => {
    requests.push(JSON.parse(options.body));
    return {
      status: 200,
      json: async () => ({
        success,
        comment: { uuid: "abc", statut: "RESOLU", mis_a_jour_le: "2026-01-01" },
        user: {},
      }),
    };
  };
  const context = vm.createContext({ document, fetch });
  const source = fs.readFileSync(path.join(__dirname, "../comment-factory.js"), "utf8");
  vm.runInContext(
    source + `
      CommentFactory.prototype.update_comment_icon = function() {};
      CommentFactory.prototype.get_comments = function(callback) {
        document.lastClicked = this.object_uuid;
        callback({ comments: [], user: {} });
      };
      CommentFactory.prototype.create_global_comment_input = function() {};
      CommentFactory.prototype.display_comment_icon = function() {};
      CommentFactory.prototype.init_comment_button = function() {};
      CommentFactory.prototype.disable_textarea = function() {};
      CommentFactory.prototype.update_status = function() {};
      new CommentFactory({ container_id: "first", object_name: "logement", object_field: "uuid", object_uuid: "1" });
      globalThis.secondFactory = new CommentFactory({ container_id: "second", object_name: "logement", object_field: "uuid", object_uuid: "2", callback_click: "refresh_opened_comments" });
    `,
    context
  );
  assert.equal(dialogs.length, 1);
  const textarea = elements.get("textarea_main_comment_modal");
  textarea.value = "Brouillon\nnon enregistré";
  textarea.setAttribute("rows", 2);
  first.onclick();
  assert.equal(document.lastClicked, "1");
  assert.equal(textarea.value, "");
  assert.equal(textarea.rows, 1);
  textarea.value = "Autre brouillon";
  second.onclick();
  assert.equal(document.lastClicked, "2");
  assert.equal(textarea.value, "");
  textarea.value = "Brouillon du même logement";
  second.onclick();
  assert.equal(textarea.value, "");
  textarea.value = "Commentaire\nà envoyer";
  textarea.setAttribute("rows", 2);
  elements.get("main_comment_modal-submit").onclick();
  await new Promise(setImmediate);
  assert.equal(requests[0].comment, "Commentaire\nà envoyer");
  assert.equal(requests[0].object_uuid, "2");
  assert.equal(textarea.value, "");
  assert.equal(textarea.rows, 1);
  assert.equal(refreshes, 1);
  success = false;
  textarea.value = "Commentaire non enregistré";
  elements.get("main_comment_modal-submit").onclick();
  await new Promise(setImmediate);
  assert.equal(textarea.value, "Commentaire non enregistré");
  assert.equal(refreshes, 1);
  success = true;
  elements.delete("refresh_opened_comments");
  textarea.value = "Sans bouton de rafraîchissement";
  elements.get("main_comment_modal-submit").onclick();
  await new Promise(setImmediate);
  assert.equal(textarea.value, "");
  elements.set("refresh_opened_comments", refresh);
  elements.set("comment_logement__uuid__2_comment_abc", { value: "Modification" });
  elements.set("comment_statut_logement__uuid__2_comment_abc", {});
  elements.set("comment_textarea_div_logement__uuid__2_comment_abc", {});
  elements.set("comment_date_logement__uuid__2_comment_abc", {});
  context.setTimeout = () => {};
  context.secondFactory.update_comment("abc", "RESOLU");
  await new Promise(setImmediate);
  assert.equal(refreshes, 2);
});
